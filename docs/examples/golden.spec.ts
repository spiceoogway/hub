// Test-harness scaffold for the DACL golden scenarios.
// References:
// - ../profiles/dacl-review-v1.golden-scenarios.md
// - ./review-state.ts

import {
  type GoldenScenario,
  type NormalizerProfile,
  type RawGitHubSnapshot,
  type ReviewStatePacket,
  reducer,
  runGoldenScenario,
} from "./review-state.ts";

const daclProfile: NormalizerProfile = {
  profileId: "alexjaniak/DACL/review-v1",
  version: "1",
  confidenceThresholds: {
    semanticBlockingMin: 75,
    needsHumanMin: 40,
    autoResolvedMin: 90,
  },
  policyOverrides: {
    strictCurrentHeadApproval: true,
    requiredCheckNames: ["dashboard-verify", "solana-bootstrap-sdk"],
    suppressRedundantPolicyFailures: true,
  },
};

function packet(overrides: Partial<ReviewStatePacket>): ReviewStatePacket {
  return {
    repo: "alexjaniak/DACL",
    prNumber: 1,
    prUrl: "https://github.com/alexjaniak/DACL/pull/1",
    state: "blocked",
    confidencePct: 95,
    headSha: "0000000",
    baseBranch: "main",
    evaluatedAt: "2026-03-07T06:30:00Z",
    profileId: daclProfile.profileId,
    profileVersion: daclProfile.version,
    blockers: [],
    actionLine: "To merge: reevaluate current head.",
    ...overrides,
  };
}

interface ReducerOrderInvariantFixture {
  name: string;
  firstRaw: RawGitHubSnapshot;
  secondRaw: RawGitHubSnapshot;
  profile: NormalizerProfile;
  expected: {
    state: ReviewStatePacket["state"];
    blockerIds: string[];
    actionKey: string;
    riskPhase: NonNullable<ReviewStatePacket["riskPhase"]>;
  };
}

export const daclGoldenScenarios: GoldenScenario[] = [
  {
    name: "clean mergeable",
    previous: packet({
      state: "blocked",
      headSha: "111aaaa",
      blockers: [
        {
          id: "failing-required-check:check:dashboard-verify",
          type: "failing-required-check",
          summary: "dashboard-verify is red",
          owner: "ci",
          resolutionCondition: "CI check dashboard-verify passes on head 111aaaa.",
          evidenceIds: [],
        },
      ],
      actionLine: "To merge: rerun dashboard-verify on head 111aaaa.",
    }),
    raw: {
      repo: "alexjaniak/DACL",
      prNumber: 1,
      prUrl: "https://github.com/alexjaniak/DACL/pull/1",
      headSha: "111aaaa",
      baseBranch: "main",
      profileId: daclProfile.profileId,
      profileVersion: daclProfile.version,
      requiredChecks: [
        { name: "dashboard-verify", status: "success" },
        { name: "solana-bootstrap-sdk", status: "success" },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "111aaaa" },
      requiredReviewersOutstanding: [],
      blockingArtifacts: [],
    },
    profile: daclProfile,
    expected: {
      state: "mergeable",
      blockerIds: [],
      actionLine: "To merge: merge current head 111aaaa now.",
      emit: true,
      notificationReason: "mergeable-flip",
    },
  },
  {
    name: "failing required check",
    previous: packet({
      state: "mergeable",
      headSha: "222bbbb",
      blockers: [],
      actionLine: "To merge: merge current head 222bbbb now.",
    }),
    raw: {
      repo: "alexjaniak/DACL",
      prNumber: 2,
      prUrl: "https://github.com/alexjaniak/DACL/pull/2",
      headSha: "222bbbb",
      baseBranch: "main",
      profileId: daclProfile.profileId,
      profileVersion: daclProfile.version,
      requiredChecks: [
        { name: "dashboard-verify", status: "failed", url: "https://github.com/alexjaniak/DACL/actions/runs/1001" },
        { name: "solana-bootstrap-sdk", status: "success" },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "222bbbb" },
      requiredReviewersOutstanding: [],
      blockingArtifacts: [],
    },
    profile: daclProfile,
    expected: {
      state: "blocked",
      blockerIds: ["failing-required-check:check:dashboard-verify"],
      actionLine: "To merge: make dashboard-verify pass on head 222bbbb.",
      emit: true,
      notificationReason: "mergeable-flip",
    },
  },
  {
    name: "pending required check no spam",
    previous: packet({
      state: "blocked",
      headSha: "333cccc",
      blockers: [
        {
          id: "pending-required-check:check:solana-bootstrap-sdk",
          type: "pending-required-check",
          summary: "solana-bootstrap-sdk still running",
          owner: "ci",
          resolutionCondition: "Required check solana-bootstrap-sdk reaches success on head 333cccc.",
          evidenceIds: [],
          appliesToHeadSha: "333cccc",
        },
      ],
      actionLine: "To merge: wait for solana-bootstrap-sdk to finish on head 333cccc.",
      actionKey: "wait.check.solana-bootstrap-sdk",
    }),
    raw: {
      repo: "alexjaniak/DACL",
      prNumber: 3,
      prUrl: "https://github.com/alexjaniak/DACL/pull/3",
      headSha: "333cccc",
      baseBranch: "main",
      profileId: daclProfile.profileId,
      profileVersion: daclProfile.version,
      requiredChecks: [
        { name: "dashboard-verify", status: "success" },
        { name: "solana-bootstrap-sdk", status: "pending", ageMinutes: 14 },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "333cccc" },
      requiredReviewersOutstanding: [],
      blockingArtifacts: [],
    },
    profile: daclProfile,
    expected: {
      state: "blocked",
      blockerIds: ["pending-required-check:check:solana-bootstrap-sdk"],
      actionLine: "To merge: wait for solana-bootstrap-sdk to finish on head 333cccc.",
      emit: false,
      notificationReason: "no-op",
    },
  },
  {
    name: "stale approval after force-push ambiguous state",
    previous: packet({
      state: "mergeable",
      headSha: "444dddd",
      blockers: [],
      actionLine: "To merge: merge current head 444dddd now.",
    }),
    raw: {
      repo: "alexjaniak/DACL",
      prNumber: 4,
      prUrl: "https://github.com/alexjaniak/DACL/pull/4",
      headSha: "555eeee",
      baseBranch: "main",
      profileId: daclProfile.profileId,
      profileVersion: daclProfile.version,
      requiredChecks: [
        { name: "dashboard-verify", status: "success" },
        { name: "solana-bootstrap-sdk", status: "success" },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "444dddd" },
      derivedSignals: {
        headShaChangedAfterLastApproval: true,
        approvalAppliesToHeadSha: false,
        reaffirmedOnCurrentHead: false,
        resolvedSemanticallyOnCurrentHead: null,
      },
      blockingArtifacts: [
        {
          id: "thread-901",
          sourceKind: "review_thread",
          author: "alexjaniak",
          semanticBlocking: true,
          intentConfidencePct: 92,
          appliesToHeadSha: "444dddd",
          resolvedInUi: true,
          resolvedSemantically: null,
          evidenceExcerpt: "must fix: auth guard missing on admin route",
        },
      ],
    },
    profile: daclProfile,
    expected: {
      state: "needs-human",
      blockerIds: ["ambiguous-state:thread:901"],
      actionLine:
        "Do not merge because prior approval was for superseded SHA; reconfirm reviewer intent on current head 555eeee.",
      emit: true,
      notificationReason: "mergeable-flip",
    },
  },
  {
    name: "blocking comment resolved on current head",
    previous: packet({
      state: "needs-human",
      headSha: "666ffff",
      blockers: [
        {
          id: "ambiguous-state:thread:901",
          type: "ambiguous-state",
          summary: "prior semantic blocker is ambiguous after head change",
          owner: "alexjaniak",
          resolutionCondition:
            "Reconfirm reviewer intent on current head 666ffff or produce positive semantic resolution on the current head.",
          evidenceIds: ["thread-901"],
          requiresHumanJudgment: true,
        },
      ],
      actionLine:
        "Do not merge because prior approval was for superseded SHA; reconfirm reviewer intent on current head 666ffff.",
    }),
    raw: {
      repo: "alexjaniak/DACL",
      prNumber: 5,
      prUrl: "https://github.com/alexjaniak/DACL/pull/5",
      headSha: "666ffff",
      baseBranch: "main",
      profileId: daclProfile.profileId,
      profileVersion: daclProfile.version,
      requiredChecks: [
        { name: "dashboard-verify", status: "success" },
        { name: "solana-bootstrap-sdk", status: "success" },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "666ffff" },
      derivedSignals: {
        headShaChangedAfterLastApproval: false,
        approvalAppliesToHeadSha: true,
        reaffirmedOnCurrentHead: true,
        resolvedSemanticallyOnCurrentHead: true,
      },
      blockingArtifacts: [
        {
          id: "thread-901",
          sourceKind: "review_thread",
          author: "alexjaniak",
          semanticBlocking: true,
          intentConfidencePct: 94,
          appliesToHeadSha: "666ffff",
          resolvedInUi: true,
          resolvedSemantically: true,
          evidenceExcerpt: "resolved on current head",
        },
      ],
    },
    profile: daclProfile,
    expected: {
      state: "mergeable",
      blockerIds: [],
      actionLine: "To merge: merge current head 666ffff now.",
      emit: true,
      notificationReason: "mergeable-flip",
    },
  },
  {
    name: "profile version change invalidates prior decision",
    previous: packet({
      state: "mergeable",
      headSha: "7779999",
      blockers: [],
      actionLine: "To merge: merge current head 7779999 now.",
    }),
    raw: {
      repo: "alexjaniak/DACL",
      prNumber: 6,
      prUrl: "https://github.com/alexjaniak/DACL/pull/6",
      headSha: "7779999",
      baseBranch: "main",
      profileId: "alexjaniak/DACL/review-v2",
      profileVersion: "2",
      requiredChecks: [
        { name: "dashboard-verify", status: "success" },
        { name: "solana-bootstrap-sdk", status: "success" },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "7779999" },
      requiredReviewersOutstanding: [],
      blockingArtifacts: [],
      policyFailures: ["policy_changed"],
    },
    profile: { ...daclProfile, profileId: "alexjaniak/DACL/review-v2", version: "2" },
    expected: {
      state: "stale",
      blockerIds: [],
      actionLine:
        "Do not merge because decision is stale after policy_changed; reevaluate current head 7779999 under profile alexjaniak/DACL/review-v2.",
      emit: true,
      notificationReason: "mergeable-flip",
    },
  },
];

export const reducerOrderInvariantFixtures: ReducerOrderInvariantFixture[] = [
  {
    name: "blocker ids are stable under artifact order changes",
    firstRaw: {
      repo: "alexjaniak/DACL",
      prNumber: 7,
      prUrl: "https://github.com/alexjaniak/DACL/pull/7",
      headSha: "888aaaa",
      baseBranch: "main",
      profileId: daclProfile.profileId,
      profileVersion: daclProfile.version,
      requiredChecks: [
        { name: "dashboard-verify", status: "success" },
        { name: "solana-bootstrap-sdk", status: "success" },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "777bbbb" },
      derivedSignals: {
        headShaChangedAfterLastApproval: true,
        approvalAppliesToHeadSha: false,
        reaffirmedOnCurrentHead: false,
        resolvedSemanticallyOnCurrentHead: null,
      },
      blockingArtifacts: [
        {
          id: "thread-12",
          sourceKind: "review_thread",
          author: "alexjaniak",
          semanticBlocking: true,
          intentConfidencePct: 92,
          appliesToHeadSha: "777bbbb",
          resolvedInUi: false,
          resolvedSemantically: null,
          evidenceExcerpt: "must fix: auth guard missing on admin route",
        },
        {
          id: "thread-19",
          sourceKind: "review_thread",
          author: "alexjaniak",
          semanticBlocking: true,
          intentConfidencePct: 90,
          appliesToHeadSha: "777bbbb",
          resolvedInUi: false,
          resolvedSemantically: null,
          evidenceExcerpt: "must fix: auth guard missing on admin route",
        },
      ],
    },
    secondRaw: {
      repo: "alexjaniak/DACL",
      prNumber: 7,
      prUrl: "https://github.com/alexjaniak/DACL/pull/7",
      headSha: "888aaaa",
      baseBranch: "main",
      profileId: daclProfile.profileId,
      profileVersion: daclProfile.version,
      requiredChecks: [
        { name: "dashboard-verify", status: "success" },
        { name: "solana-bootstrap-sdk", status: "success" },
      ],
      latestValidApproval: { author: "alexjaniak", commitId: "777bbbb" },
      derivedSignals: {
        headShaChangedAfterLastApproval: true,
        approvalAppliesToHeadSha: false,
        reaffirmedOnCurrentHead: false,
        resolvedSemanticallyOnCurrentHead: null,
      },
      blockingArtifacts: [
        {
          id: "thread-19",
          sourceKind: "review_thread",
          author: "alexjaniak",
          semanticBlocking: true,
          intentConfidencePct: 90,
          appliesToHeadSha: "777bbbb",
          resolvedInUi: false,
          resolvedSemantically: null,
          evidenceExcerpt: "must fix: auth guard missing on admin route",
        },
        {
          id: "thread-12",
          sourceKind: "review_thread",
          author: "alexjaniak",
          semanticBlocking: true,
          intentConfidencePct: 92,
          appliesToHeadSha: "777bbbb",
          resolvedInUi: false,
          resolvedSemantically: null,
          evidenceExcerpt: "must fix: auth guard missing on admin route",
        },
      ],
    },
    profile: daclProfile,
    expected: {
      state: "needs-human",
      blockerIds: ["ambiguous-state:thread:12", "ambiguous-state:thread:19"],
      actionKey: "reconfirm.intent.thread-12.head.888aaaa",
      riskPhase: "ambiguous",
    },
  },
];

export function runAllGoldenScenarios(reduce = reducer) {
  return daclGoldenScenarios.map((scenario) => ({
    name: scenario.name,
    ...runGoldenScenario(scenario, reduce),
  }));
}

export function runReducerOrderInvariantFixtures(reduce = reducer) {
  return reducerOrderInvariantFixtures.map((fixture) => {
    const first = reduce(fixture.firstRaw, fixture.profile);
    const second = reduce(fixture.secondRaw, fixture.profile);
    const diffs: string[] = [];

    const firstIds = [...first.blockers.map((blocker) => blocker.id)].sort();
    const secondIds = [...second.blockers.map((blocker) => blocker.id)].sort();
    const expectedIds = [...fixture.expected.blockerIds].sort();

    if (first.state !== fixture.expected.state || second.state !== fixture.expected.state) {
      diffs.push(`state mismatch: expected=${fixture.expected.state} actual=${first.state}/${second.state}`);
    }

    if (JSON.stringify(firstIds) !== JSON.stringify(expectedIds)) {
      diffs.push(`first blocker ids mismatch: expected=${expectedIds.join(",")} actual=${firstIds.join(",")}`);
    }

    if (JSON.stringify(secondIds) !== JSON.stringify(expectedIds)) {
      diffs.push(`second blocker ids mismatch: expected=${expectedIds.join(",")} actual=${secondIds.join(",")}`);
    }

    if (JSON.stringify(firstIds) !== JSON.stringify(secondIds)) {
      diffs.push(`order invariance failed: first=${firstIds.join(",")} second=${secondIds.join(",")}`);
    }

    if (first.actionKey !== fixture.expected.actionKey || second.actionKey !== fixture.expected.actionKey) {
      diffs.push(`actionKey mismatch: expected=${fixture.expected.actionKey} actual=${first.actionKey}/${second.actionKey}`);
    }

    if (first.riskPhase !== fixture.expected.riskPhase || second.riskPhase !== fixture.expected.riskPhase) {
      diffs.push(`riskPhase mismatch: expected=${fixture.expected.riskPhase} actual=${first.riskPhase}/${second.riskPhase}`);
    }

    return {
      name: fixture.name,
      pass: diffs.length === 0,
      diffs,
      first,
      second,
    };
  });
}

export function runRandomizedReducerOrderInvariantFixtures(reduce = reducer, rounds = 25) {
  return reducerOrderInvariantFixtures.map((fixture) => {
    const baseline = reduce(fixture.firstRaw, fixture.profile);
    const baselineIds = [...baseline.blockers.map((blocker) => blocker.id)].sort();
    const diffs: string[] = [];

    for (let seed = 1; seed <= rounds; seed += 1) {
      const shuffled = {
        ...fixture.firstRaw,
        blockingArtifacts: shuffleWithSeed([...(fixture.firstRaw.blockingArtifacts ?? [])], seed),
      };
      const result = reduce(shuffled, fixture.profile);
      const resultIds = [...result.blockers.map((blocker) => blocker.id)].sort();

      if (JSON.stringify(resultIds) !== JSON.stringify(baselineIds)) {
        diffs.push(`seed ${seed} blocker ids mismatch: baseline=${baselineIds.join(",")} actual=${resultIds.join(",")}`);
        break;
      }

      if (result.state !== baseline.state) {
        diffs.push(`seed ${seed} state mismatch: baseline=${baseline.state} actual=${result.state}`);
        break;
      }

      if (result.actionKey !== baseline.actionKey) {
        diffs.push(`seed ${seed} actionKey mismatch: baseline=${baseline.actionKey} actual=${result.actionKey}`);
        break;
      }

      if (result.riskPhase !== baseline.riskPhase) {
        diffs.push(`seed ${seed} riskPhase mismatch: baseline=${baseline.riskPhase} actual=${result.riskPhase}`);
        break;
      }
    }

    return {
      name: `${fixture.name} (randomized ${rounds}x)`,
      pass: diffs.length === 0,
      diffs,
      baseline,
    };
  });
}

function shuffleWithSeed<T>(values: T[], seed: number): T[] {
  const result = [...values];
  let state = seed >>> 0;

  const next = () => {
    state = (state * 1664525 + 1013904223) >>> 0;
    return state / 0x100000000;
  };

  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(next() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }

  return result;
}

// Optional tiny runner when executed directly under a TS-aware runtime.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const maybeProcess = globalThis as any;
if (typeof maybeProcess?.argv !== "undefined" && maybeProcess.argv[1]?.endsWith("golden.spec.ts")) {
  const results = [...runAllGoldenScenarios(), ...runReducerOrderInvariantFixtures(), ...runRandomizedReducerOrderInvariantFixtures()];
  for (const result of results) {
    const mark = result.pass ? "PASS" : "FAIL";
    // eslint-disable-next-line no-console
    console.log(mark, result.name, result.diffs);
  }
}
