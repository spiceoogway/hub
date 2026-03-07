// Implementation scaffold for the PR review control plane.
// References:
// - ../pr-review-state-v0.md
// - ../pr-blocker-reducer-v0.1.md
// - ../notification-transition-matrix-v0.1.md
// - ../pr-normalizer-profile-v0.1.md

export type ReviewState = "mergeable" | "blocked" | "stale" | "needs-human";

// Deliberate choice: keep blocker types aligned with the canonical docs instead of
// compressing them too early. Pending checks and semantic blockers need distinct
// types for no-spam behavior and accurate action lines.
export type BlockerType =
  | "failing-required-check"
  | "pending-required-check"
  | "missing-approval"
  | "blocking-review"
  | "blocking-comment"
  | "ambiguous-state"
  | "policy-failure";

// Deliberate choice: use a directional mergeable flip rather than boolean.
// The notifier needs to distinguish became_mergeable vs ceased_mergeable.
export type MergeableFlip = "became_mergeable" | "ceased_mergeable" | "none";

export type ConfidenceDropBucket = "none" | "minor" | "threshold_cross" | "severe";

// Optional coarse risk phase for notification bucketing.
// This exists because numeric confidence delta alone misses class changes like:
// ambiguous -> explicit trusted block on current head.
export type RiskPhase = "steady" | "ambiguous" | "explicit-blocking" | "contradictory-current-head";

export interface Blocker {
  id: string; // stable, diff-safe
  type: BlockerType;
  summary: string;
  owner?: string;
  openedAt?: string; // ISO
  resolutionCondition: string;
  confidencePct?: number;
  evidenceIds: string[];
  requiresHumanJudgment?: boolean;
  appliesToHeadSha?: string | null;
}

export interface BlockingArtifact {
  id: string;
  sourceKind:
    | "review_state"
    | "review_thread"
    | "issue_comment"
    | "pr_comment"
    | "policy_bot"
    | "external";
  author?: string;
  semanticBlocking?: boolean;
  formalBlocking?: boolean;
  intentConfidencePct?: number;
  appliesToHeadSha?: string | null;
  supersededByHeadSha?: string | null;
  resolvedInUi?: boolean;
  resolvedSemantically?: boolean | null;
  evidenceExcerpt?: string;
}

export interface RequiredCheck {
  name: string;
  status: "success" | "pending" | "failed" | "missing" | "neutral" | "skipped" | "cancelled";
  url?: string;
  ageMinutes?: number;
}

export interface ReviewEvent {
  author: string;
  state: "APPROVED" | "CHANGES_REQUESTED" | "COMMENTED" | "DISMISSED";
  commitId?: string | null;
  submittedAt: string;
}

export interface ApprovalRef {
  author: string;
  commitId: string;
}

export interface DerivedSignals {
  headShaChangedAfterLastApproval: boolean | null;
  approvalAppliesToHeadSha: boolean | null;
  reaffirmedOnCurrentHead: boolean;
  resolvedSemanticallyOnCurrentHead: boolean | null;
}

export interface RawGitHubSnapshot {
  repo: string;
  prNumber: number;
  prUrl: string;
  headSha: string;
  baseBranch: string;
  baseSha?: string;
  evaluatedAt?: string;
  profileId: string;
  profileVersion: string;
  requiredChecks: RequiredCheck[];
  requiredReviewersOutstanding?: string[];
  latestValidApproval?: ApprovalRef | null;
  reviewEvents?: ReviewEvent[];
  blockingArtifacts?: BlockingArtifact[];
  derivedSignals?: DerivedSignals;
  policyFailures?: string[];
}

export interface NormalizerProfile {
  profileId: string;
  version: string;
  confidenceThresholds: {
    semanticBlockingMin: number;
    needsHumanMin: number;
    autoResolvedMin: number;
  };
  policyOverrides: {
    strictCurrentHeadApproval: boolean;
    requiredCheckNames?: string[];
    suppressRedundantPolicyFailures?: boolean;
  };
}

export interface ReviewStatePacket {
  repo: string;
  prNumber: number;
  prUrl: string;
  state: ReviewState;
  confidencePct: number;
  headSha: string;
  baseBranch: string;
  evaluatedAt: string;
  profileId: string;
  profileVersion: string;
  blockers: Blocker[];
  actionLine: string;
  // Optional coarse risk phase for notifier bucketing.
  riskPhase?: RiskPhase;
  // Machine token for notification/dedupe semantics.
  // Recommended namespace examples:
  // - merge.now
  // - wait.check.dashboard-verify
  // - need.approval.alexjaniak
  // - reconfirm.intent.thread-901.head.555eeee
  // If omitted, the notifier derives a coarse fallback from state + blocker ids.
  actionKey?: string;
}

export interface NotificationTuple {
  oldState: ReviewState;
  newState: ReviewState;
  blockerSetChanged: boolean;
  actionKeyChanged: boolean;
  confidenceDropBucket: ConfidenceDropBucket;
  mergeableFlip: MergeableFlip;
}

export interface NotificationDecision {
  emit: boolean;
  reason: "state-change" | "blocker-set-change" | "action-line-change" | "confidence-drop" | "mergeable-flip" | "no-op";
  priority: "low" | "normal" | "high";
}

export interface RiskPhaseInvariantResult {
  valid: boolean;
  reason: "ok" | "risk-phase-improved-without-supporting-change";
}

export interface BlockerDiffResult {
  changed: boolean;
  added: Blocker[];
  removed: Blocker[];
  modified: Array<{ before: Blocker; after: Blocker }>;
}

export interface GoldenScenario {
  name: string;
  previous: ReviewStatePacket;
  raw: RawGitHubSnapshot;
  profile: NormalizerProfile;
  expected: {
    state: ReviewState;
    blockerIds: string[];
    actionLine: string;
    emit: boolean;
    notificationReason?: NotificationDecision["reason"];
  };
}

export function reducer(raw: RawGitHubSnapshot, profile: NormalizerProfile): ReviewStatePacket {
  const evaluatedAt = raw.evaluatedAt ?? new Date().toISOString();

  const extractDerivedSignals = (snapshot: RawGitHubSnapshot): DerivedSignals => {
    const latestApproval = snapshot.latestValidApproval ?? null;

    const headShaChangedAfterLastApproval = latestApproval?.commitId
      ? latestApproval.commitId !== snapshot.headSha
      : null;

    const approvalAppliesToHeadSha = latestApproval?.commitId
      ? latestApproval.commitId === snapshot.headSha
      : null;

    let reaffirmedOnCurrentHead = false;
    if (approvalAppliesToHeadSha === true) reaffirmedOnCurrentHead = true;
    if (!reaffirmedOnCurrentHead && snapshot.reviewEvents?.length) {
      reaffirmedOnCurrentHead = snapshot.reviewEvents.some(
        (event) => event.state === "APPROVED" && !!event.commitId && event.commitId === snapshot.headSha,
      );
    }

    const artifacts = snapshot.blockingArtifacts ?? [];
    const currentHeadArtifacts = artifacts.filter(
      (artifact) => !artifact.appliesToHeadSha || artifact.appliesToHeadSha === snapshot.headSha,
    );

    let resolvedSemanticallyOnCurrentHead: boolean | null = null;
    const semanticCurrent = currentHeadArtifacts.filter((artifact) => artifact.semanticBlocking === true);

    if (semanticCurrent.length > 0) {
      const anyUnresolved = semanticCurrent.some(
        (artifact) => artifact.resolvedSemantically === false || artifact.resolvedInUi === false,
      );
      const allResolved = semanticCurrent.every((artifact) => artifact.resolvedSemantically === true);

      if (anyUnresolved) resolvedSemanticallyOnCurrentHead = false;
      else if (allResolved) resolvedSemanticallyOnCurrentHead = true;
      else resolvedSemanticallyOnCurrentHead = null;
    }

    return {
      headShaChangedAfterLastApproval,
      approvalAppliesToHeadSha,
      reaffirmedOnCurrentHead,
      resolvedSemanticallyOnCurrentHead,
    };
  };

  const derived = raw.derivedSignals ?? extractDerivedSignals(raw);

  const blockers: Blocker[] = [];
  const upsertBlocker = (blocker: Blocker) => {
    const existing = blockers.find((current) => current.id === blocker.id);
    if (!existing) {
      blockers.push(blocker);
      return;
    }

    existing.evidenceIds = sorted([...new Set([...existing.evidenceIds, ...blocker.evidenceIds])]);
    if (blocker.confidencePct != null) {
      existing.confidencePct =
        existing.confidencePct == null ? blocker.confidencePct : Math.max(existing.confidencePct, blocker.confidencePct);
    }
    existing.requiresHumanJudgment =
      Boolean(existing.requiresHumanJudgment) || Boolean(blocker.requiresHumanJudgment);
  };

  const requiredCheckNames =
    profile.policyOverrides.requiredCheckNames && profile.policyOverrides.requiredCheckNames.length > 0
      ? profile.policyOverrides.requiredCheckNames
      : Array.from(new Set(raw.requiredChecks.map((check) => check.name)));

  for (const name of requiredCheckNames) {
    const check = raw.requiredChecks.find((current) => current.name === name);
    const status = check?.status ?? "missing";

    if (status === "failed" || status === "missing" || status === "cancelled") {
      upsertBlocker({
        id: `failing-required-check:check:${name}`,
        type: "failing-required-check",
        owner: "ci",
        summary: `Required check failing or missing: ${name}`,
        resolutionCondition: `CI check ${name} passes on head ${raw.headSha}.`,
        evidenceIds: [check?.url ?? `required-check:${name}`],
        appliesToHeadSha: raw.headSha,
      });
      continue;
    }

    if (status === "pending") {
      upsertBlocker({
        id: `pending-required-check:check:${name}`,
        type: "pending-required-check",
        owner: "ci",
        summary: `Required check pending: ${name}`,
        resolutionCondition: `Required check ${name} reaches success on head ${raw.headSha}.`,
        evidenceIds: [check?.url ?? `required-check:${name}`],
        appliesToHeadSha: raw.headSha,
      });
    }
  }

  for (const reviewer of raw.requiredReviewersOutstanding ?? []) {
    upsertBlocker({
      id: `missing-approval:reviewer:${reviewer}`,
      type: "missing-approval",
      owner: reviewer,
      summary: `Required reviewer outstanding: ${reviewer}`,
      resolutionCondition: `Obtain approval from ${reviewer}.`,
      evidenceIds: [`required-reviewer:${reviewer}`],
      appliesToHeadSha: raw.headSha,
    });
  }

  const strongOldHeadSemanticArtifacts = (raw.blockingArtifacts ?? []).filter((artifact) => {
    const semanticConf = artifact.intentConfidencePct ?? 0;
    const appliesToCurrentHead = !artifact.appliesToHeadSha || artifact.appliesToHeadSha === raw.headSha;
    return artifact.semanticBlocking === true && semanticConf >= profile.confidenceThresholds.semanticBlockingMin && !appliesToCurrentHead;
  });

  if (profile.policyOverrides.strictCurrentHeadApproval) {
    if (!raw.latestValidApproval) {
      upsertBlocker({
        id: "missing-approval:reviewer:current-head",
        type: "missing-approval",
        summary: "No valid approval found.",
        resolutionCondition: "Obtain approval on current head SHA.",
        evidenceIds: ["approval:none"],
        appliesToHeadSha: raw.headSha,
      });
    } else if (derived.approvalAppliesToHeadSha === false && !derived.reaffirmedOnCurrentHead) {
      if (strongOldHeadSemanticArtifacts.length === 0) {
        upsertBlocker({
          id: `ambiguous-state:review:${raw.latestValidApproval.author}`,
          type: "ambiguous-state",
          owner: raw.latestValidApproval.author,
          summary: "Prior approval targets superseded head SHA.",
          resolutionCondition: `Reconfirm reviewer intent on current head ${raw.headSha}.`,
          confidencePct: Math.max(profile.confidenceThresholds.needsHumanMin, 70),
          evidenceIds: [`approval:${raw.latestValidApproval.commitId}`, `head:${raw.headSha}`],
          requiresHumanJudgment: true,
          appliesToHeadSha: raw.headSha,
        });
      }
    }
  }

  for (const artifact of raw.blockingArtifacts ?? []) {
    const appliesToCurrentHead = !artifact.appliesToHeadSha || artifact.appliesToHeadSha === raw.headSha;
    const semanticConf = artifact.intentConfidencePct ?? 0;
    const semanticStrong =
      artifact.semanticBlocking === true && semanticConf >= profile.confidenceThresholds.semanticBlockingMin;
    const explicitResolved = artifact.resolvedSemantically === true;

    if (appliesToCurrentHead) {
      if (artifact.formalBlocking === true && !explicitResolved) {
        upsertBlocker({
          id: `blocking-${artifact.sourceKind === "review_state" ? "review" : "comment"}:artifact:${artifact.id}`,
          type: artifact.sourceKind === "review_state" ? "blocking-review" : "blocking-comment",
          summary: artifact.evidenceExcerpt ?? "Formal blocking signal present.",
          owner: artifact.author,
          resolutionCondition: "Resolve blocking review/comment on current head.",
          evidenceIds: [artifact.id],
          appliesToHeadSha: raw.headSha,
        });
      } else if (semanticStrong && !explicitResolved) {
        upsertBlocker({
          id: `blocking-comment:artifact:${artifact.id}`,
          type: "blocking-comment",
          summary: artifact.evidenceExcerpt ?? "Semantic blocking concern unresolved.",
          owner: artifact.author,
          resolutionCondition: "Resolve semantic blocker on current head.",
          confidencePct: semanticConf,
          evidenceIds: [artifact.id],
          appliesToHeadSha: raw.headSha,
        });
      }
      continue;
    }

    if (semanticStrong && !derived.reaffirmedOnCurrentHead && derived.resolvedSemanticallyOnCurrentHead !== true) {
      const threadKey = extractThreadKey(artifact.id);
      upsertBlocker({
        id: `ambiguous-state:thread:${threadKey}`,
        type: "ambiguous-state",
        summary: "Semantic blocker references superseded head; intent on current head is ambiguous.",
        owner: artifact.author,
        resolutionCondition: `Reconfirm reviewer intent on current head ${raw.headSha}.`,
        confidencePct: Math.max(profile.confidenceThresholds.needsHumanMin, semanticConf),
        evidenceIds: [artifact.id, `head:${raw.headSha}`],
        requiresHumanJudgment: true,
        appliesToHeadSha: raw.headSha,
      });
    }
  }

  const policyFailures = raw.policyFailures ?? [];
  const hasPolicyChanged =
    raw.profileId !== profile.profileId ||
    raw.profileVersion !== profile.version ||
    policyFailures.some((failure) => /policy_changed|profile_changed/i.test(failure));

  for (const policyFailure of policyFailures) {
    if (/policy_changed|profile_changed/i.test(policyFailure)) continue;

    if (
      profile.policyOverrides.suppressRedundantPolicyFailures &&
      /required[_ -]?check/i.test(policyFailure) &&
      blockers.some((blocker) => blocker.type === "failing-required-check" || blocker.type === "pending-required-check")
    ) {
      continue;
    }

    upsertBlocker({
      id: `policy-failure:policy:${policyFailure}`,
      type: "policy-failure",
      summary: `Policy failure: ${policyFailure}`,
      resolutionCondition: `Satisfy policy rule "${policyFailure}".`,
      evidenceIds: [`policy:${policyFailure}`],
      appliesToHeadSha: raw.headSha,
    });
  }

  const hasNeedsHuman = blockers.some(
    (blocker) => blocker.type === "ambiguous-state" || blocker.requiresHumanJudgment === true,
  );
  const hasBlocking = blockers.length > 0;

  let state: ReviewState;
  if (hasNeedsHuman) state = "needs-human";
  else if (hasPolicyChanged) state = "stale";
  else if (hasBlocking) state = "blocked";
  else state = "mergeable";

  const blockerPriority: Record<BlockerType, number> = {
    "ambiguous-state": 0,
    "policy-failure": 1,
    "failing-required-check": 2,
    "missing-approval": 3,
    "blocking-review": 4,
    "blocking-comment": 5,
    "pending-required-check": 6,
  };
  blockers.sort((a, b) => {
    const aPriority = blockerPriority[a.type] ?? 99;
    const bPriority = blockerPriority[b.type] ?? 99;
    if (aPriority !== bPriority) return aPriority - bPriority;
    return a.id.localeCompare(b.id);
  });

  const failing = blockers.find((blocker) => blocker.type === "failing-required-check");
  const pending = blockers.find((blocker) => blocker.type === "pending-required-check");
  const missingApproval = blockers.find((blocker) => blocker.type === "missing-approval");
  const policy = blockers.find((blocker) => blocker.type === "policy-failure");
  const blockingReview = blockers.find((blocker) => blocker.type === "blocking-review");
  const blockingComment = blockers.find((blocker) => blocker.type === "blocking-comment");
  const ambiguous = blockers.find((blocker) => blocker.type === "ambiguous-state");

  let actionLine = `To merge: merge current head ${raw.headSha} now.`;
  let actionKey = "merge.now";

  if (state === "stale") {
    actionLine = `Do not merge because decision is stale after policy_changed; reevaluate current head ${raw.headSha} under profile ${profile.profileId}.`;
    actionKey = "policy.policy_changed";
  } else if (state === "needs-human") {
    actionLine = `Do not merge because prior approval was for superseded SHA; reconfirm reviewer intent on current head ${raw.headSha}.`;
    actionKey = ambiguous
      ? `reconfirm.intent.${normalizeToken(ambiguous.id.replace(/^ambiguous-state:/, ""))}.head.${raw.headSha}`
      : `reconfirm.intent.current-head.${raw.headSha}`;
  } else if (state === "blocked") {
    if (failing) {
      const checkName = extractCheckName(failing.id);
      actionLine = `To merge: make ${checkName} pass on head ${raw.headSha}.`;
      actionKey = `fix.check.${checkName}`;
    } else if (pending) {
      const checkName = extractCheckName(pending.id);
      actionLine = `To merge: wait for ${checkName} to finish on head ${raw.headSha}.`;
      actionKey = `wait.check.${checkName}`;
    } else if (missingApproval?.owner) {
      actionLine = `To merge: obtain approval from ${missingApproval.owner}.`;
      actionKey = `need.approval.${normalizeToken(missingApproval.owner)}`;
    } else if (policy) {
      const rule = normalizeToken(policy.id.replace(/^policy-failure:policy:/, ""));
      actionLine = policy.resolutionCondition;
      actionKey = `policy.${rule}`;
    } else if (blockingReview || blockingComment) {
      actionLine = (blockingReview ?? blockingComment)?.resolutionCondition ?? "Resolve blockers before merge.";
      actionKey = `resolve.blockers.${raw.prNumber}`;
    }
  }

  let riskPhase: RiskPhase = "steady";
  if (state === "needs-human") riskPhase = "ambiguous";
  if (blockers.some((blocker) => blocker.type === "blocking-review" || blocker.type === "blocking-comment")) {
    riskPhase = "explicit-blocking";
  }
  if (
    state === "needs-human" &&
    blockers.some((blocker) => blocker.type === "ambiguous-state") &&
    blockers.some((blocker) => blocker.type === "blocking-review" || blocker.type === "blocking-comment")
  ) {
    riskPhase = "contradictory-current-head";
  }

  let confidencePct = 96;
  if (state === "blocked") {
    if (pending && !failing && !missingApproval && !policy && !blockingReview && !blockingComment) confidencePct = 95;
    else if (missingApproval && !failing && !policy && !blockingReview && !blockingComment) confidencePct = 90;
    else confidencePct = 82;
  }
  if (state === "stale") confidencePct = 68;
  if (state === "needs-human") confidencePct = 58;

  return {
    repo: raw.repo,
    prNumber: raw.prNumber,
    prUrl: raw.prUrl,
    state,
    confidencePct,
    headSha: raw.headSha,
    baseBranch: raw.baseBranch,
    evaluatedAt,
    profileId: profile.profileId,
    profileVersion: profile.version,
    blockers,
    actionLine,
    riskPhase,
    actionKey,
  };
}

export function blockerDiff(prev: Blocker[], next: Blocker[]): BlockerDiffResult {
  const prevById = new Map(prev.map((blocker) => [blocker.id, blocker]));
  const nextById = new Map(next.map((blocker) => [blocker.id, blocker]));

  const added: Blocker[] = [];
  const removed: Blocker[] = [];
  const modified: Array<{ before: Blocker; after: Blocker }> = [];

  for (const [id, before] of prevById) {
    const after = nextById.get(id);
    if (!after) {
      removed.push(before);
      continue;
    }
    if (hasMaterialBlockerChange(before, after)) {
      modified.push({ before, after });
    }
  }

  for (const [id, after] of nextById) {
    if (!prevById.has(id)) {
      added.push(after);
    }
  }

  return {
    changed: added.length > 0 || removed.length > 0 || modified.length > 0,
    added,
    removed,
    modified,
  };
}

export function buildNotificationTuple(previous: ReviewStatePacket, next: ReviewStatePacket): NotificationTuple {
  const diff = blockerDiff(previous.blockers, next.blockers);

  return {
    oldState: previous.state,
    newState: next.state,
    blockerSetChanged: diff.changed,
    actionKeyChanged: getComparableActionKey(previous) !== getComparableActionKey(next),
    confidenceDropBucket: getConfidenceDropBucket(
      previous.confidencePct,
      next.confidencePct,
      previous.riskPhase,
      next.riskPhase,
    ),
    mergeableFlip: getMergeableFlip(previous.state, next.state),
  };
}

export function notificationDecision(tuple: NotificationTuple): NotificationDecision {
  if (tuple.mergeableFlip === "became_mergeable" || tuple.mergeableFlip === "ceased_mergeable") {
    return { emit: true, reason: "mergeable-flip", priority: "high" };
  }

  if (tuple.oldState !== tuple.newState) {
    return {
      emit: true,
      reason: "state-change",
      priority: tuple.newState === "needs-human" || tuple.newState === "stale" ? "high" : "normal",
    };
  }

  if (tuple.blockerSetChanged) {
    return { emit: true, reason: "blocker-set-change", priority: "normal" };
  }

  if (tuple.actionKeyChanged) {
    return { emit: true, reason: "action-line-change", priority: "normal" };
  }

  // Hard risk-escalation rule:
  // even if state, blocker ids, and action key are unchanged,
  // a threshold-crossing or severe confidence drop must emit.
  if (tuple.confidenceDropBucket === "threshold_cross" || tuple.confidenceDropBucket === "severe") {
    return {
      emit: true,
      reason: "confidence-drop",
      priority: tuple.confidenceDropBucket === "severe" ? "high" : "normal",
    };
  }

  return { emit: false, reason: "no-op", priority: "low" };
}

export function validateRiskPhaseInvariant(
  previous: ReviewStatePacket,
  next: ReviewStatePacket,
): RiskPhaseInvariantResult {
  const previousPhase = previous.riskPhase ?? "steady";
  const nextPhase = next.riskPhase ?? previousPhase;

  if (riskPhaseSeverity(nextPhase) < riskPhaseSeverity(previousPhase)) {
    const blockersChanged = blockerDiff(previous.blockers, next.blockers).changed;
    const actionKeyChanged = getComparableActionKey(previous) !== getComparableActionKey(next);
    const evidenceChanged = blockerEvidenceSignature(previous.blockers) !== blockerEvidenceSignature(next.blockers);

    if (!blockersChanged && !actionKeyChanged && !evidenceChanged) {
      return {
        valid: false,
        reason: "risk-phase-improved-without-supporting-change",
      };
    }
  }

  return { valid: true, reason: "ok" };
}

export function runGoldenScenario(
  scenario: GoldenScenario,
  reduce: typeof reducer = reducer,
): { pass: boolean; diffs: string[] } {
  const next = reduce(scenario.raw, scenario.profile);
  const tuple = buildNotificationTuple(scenario.previous, next);
  const notify = notificationDecision(tuple);

  const diffs: string[] = [];
  const actualIds = sorted(next.blockers.map((blocker) => blocker.id));
  const expectedIds = sorted(scenario.expected.blockerIds);

  if (next.state !== scenario.expected.state) {
    diffs.push(`state mismatch: expected=${scenario.expected.state} actual=${next.state}`);
  }

  if (JSON.stringify(actualIds) !== JSON.stringify(expectedIds)) {
    diffs.push(`blocker ids mismatch: expected=${expectedIds.join(",")} actual=${actualIds.join(",")}`);
  }

  if (normalizeForCompare(next.actionLine) !== normalizeForCompare(scenario.expected.actionLine)) {
    diffs.push(`action line mismatch: expected=${scenario.expected.actionLine} actual=${next.actionLine}`);
  }

  if (notify.emit !== scenario.expected.emit) {
    diffs.push(`notify.emit mismatch: expected=${scenario.expected.emit} actual=${notify.emit}`);
  }

  if (scenario.expected.notificationReason && notify.reason !== scenario.expected.notificationReason) {
    diffs.push(`notify.reason mismatch: expected=${scenario.expected.notificationReason} actual=${notify.reason}`);
  }

  return { pass: diffs.length === 0, diffs };
}

function hasMaterialBlockerChange(before: Blocker, after: Blocker): boolean {
  return JSON.stringify(materialBlockerShape(before)) !== JSON.stringify(materialBlockerShape(after));
}

function materialBlockerShape(blocker: Blocker) {
  return {
    type: blocker.type,
    owner: blocker.owner ?? null,
    resolutionCondition: normalizeForCompare(blocker.resolutionCondition),
    requiresHumanJudgment: blocker.requiresHumanJudgment ?? false,
    appliesToHeadSha: blocker.appliesToHeadSha ?? null,
  };
}

function blockerEvidenceSignature(blockers: Blocker[]): string {
  return sorted(
    blockers.flatMap((blocker) => blocker.evidenceIds.map((evidenceId) => `${blocker.id}:${evidenceId}`)),
  ).join("|");
}

function extractThreadKey(value: string): string {
  const match = value.match(/(?:thread-|thread:)?([a-zA-Z0-9._-]+)$/);
  return match?.[1] ?? normalizeToken(value);
}

function extractCheckName(value: string): string {
  const match = value.match(/^(?:failing-required-check|pending-required-check):check:(.+)$/);
  return match?.[1] ?? value;
}

function normalizeToken(value: string): string {
  return value.replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-+|-+$/g, "");
}

function normalizeForCompare(value: string): string {
  return value.trim().replace(/\s+/g, " ");
}

function getComparableActionKey(packet: ReviewStatePacket): string {
  if (packet.actionKey) return packet.actionKey;
  return `${packet.state}|${sorted(packet.blockers.map((blocker) => blocker.id)).join(",")}`;
}

function getMergeableFlip(oldState: ReviewState, newState: ReviewState): MergeableFlip {
  if (oldState !== "mergeable" && newState === "mergeable") return "became_mergeable";
  if (oldState === "mergeable" && newState !== "mergeable") return "ceased_mergeable";
  return "none";
}

function getConfidenceDropBucket(
  previous: number,
  next: number,
  previousRiskPhase: RiskPhase = "steady",
  nextRiskPhase: RiskPhase = previousRiskPhase,
): ConfidenceDropBucket {
  // Phase transitions override raw numeric delta.
  // Example: ambiguous -> explicit-blocking should page even if the score drop is only moderate.
  if (riskPhaseSeverity(nextRiskPhase) > riskPhaseSeverity(previousRiskPhase)) {
    return "severe";
  }

  if (next >= previous) return "none";

  const previousBand = confidenceBand(previous);
  const nextBand = confidenceBand(next);
  const drop = previous - next;

  if (nextBand !== previousBand) return "threshold_cross";
  if (next < 60 || drop >= 25) return "severe";
  if (drop >= 1) return "minor";
  return "none";
}

function riskPhaseSeverity(phase: RiskPhase): number {
  switch (phase) {
    case "steady":
      return 0;
    case "ambiguous":
      return 1;
    case "explicit-blocking":
      return 2;
    case "contradictory-current-head":
      return 3;
  }
}

function confidenceBand(value: number): "high" | "medium" | "low" {
  if (value >= 85) return "high";
  if (value >= 60) return "medium";
  return "low";
}

function sorted(values: string[]): string[] {
  return [...values].sort();
}
