# TPM Automation Feature Roadmap

## Phase 1: MVP Success (Complete ✓)

**Objective:** Prove the plumbing works.

**What We Shipped:**
- Autonomous prompt chain execution (tasks 00 → 01 → 02 → 03)
- Cross-platform CLI agent compatibility (Claude, Grok, Gemini, Codex verified)
- Zero-friction GitHub API integration (pre-approved `gh` tool operations)
- Basic utility: Daily stand-up report generation

**Key Achievement:**
We validated the **technical foundation**. The automation infrastructure is sound. The permission model works. The task chain pattern is portable across AI platforms.

**What We Learned:**
The stand-up report itself is minimal (by design), but it demonstrates:
- Agent can read GitHub state autonomously
- Agent can synthesize information across issues/PRs
- Agent can write back to GitHub (issue comments)
- Agent can persist state between sessions
- Shell script wrapper eliminates friction

---

## Phase 2: Evolution Strategy (Next)

**Guiding Principle:** Small, testable increments.

**Current State:**
- Infrastructure: **Proven** ✓
- Utility: **Minimal** (stand-up reports provide context, but not actionable intelligence)
- Roadmap: **Undefined** (we need to prioritize what "useful" means)

**What We Need:**
A **feature roadmap** that defines:
1. **What capabilities to add** (in priority order)
2. **How each capability increases utility** (measurable value)
3. **How to test each increment** (validation criteria)
4. **What stays minimal** (scope boundaries to prevent bloat)

**Strategic Questions for Roadmap:**
- What decisions does the TPM need to make autonomously vs. flag for human review?
- What triggers should invoke the TPM (daily cron? PR events? on-demand)?
- What intelligence does the TPM need to provide strategic value (not just data regurgitation)?
- How does the TPM integrate with existing workflows (Git hooks? CI/CD? Issue templates)?

**Success Criteria for Roadmap:**
- Each feature is **independently testable**
- Each feature **adds measurable value** (reduces manual work, surfaces insights, prevents misalignment)
- Features are **sequenced by dependency** (build incrementally, no big bang)
- Scope remains **ruthlessly minimal** (delete readily, complexity is a liability)

---

## Proposed Feature Pipeline (To Be Prioritized)

### Feature Ideas (Unsorted)

#### F1: Gate 1 Alignment Scoring
**Value:** Quantify how each open issue/PR contributes to Gate 1 objective.
**Acceptance Criteria:** Each work item gets a score (0-10) with rationale comment.
**Complexity:** M
**Dependencies:** None (builds on MVP)

#### F2: Automated Misalignment Flagging
**Value:** Post comments on issues/PRs that deviate from Gate 1 critical path.
**Acceptance Criteria:** TPM posts comment with specific rationale + reference to `docs/VALIDATION_GATES.md`.
**Complexity:** M
**Dependencies:** F1 (scoring logic)

#### F3: Weekly Progress Summary
**Value:** Higher-level strategic view (vs. daily tactical stand-up).
**Acceptance Criteria:** Weekly report shows trend (velocity toward Gate 1, blockers, focus drift).
**Complexity:** S
**Dependencies:** None (aggregates daily stand-ups)

#### F4: CI/CD Integration
**Value:** TPM runs automatically on PR creation/update, posts assessment comment.
**Acceptance Criteria:** GitHub Actions workflow triggers TPM analysis, posts to PR.
**Complexity:** L
**Dependencies:** F2 (alignment logic must be stable)

#### F5: Slack/Discord Notifications
**Value:** Push stand-up reports to team chat for visibility.
**Acceptance Criteria:** Daily stand-up posted to configured channel.
**Complexity:** S
**Dependencies:** None (extends output, doesn't change logic)

#### F6: Intelligent Task Decomposition Suggestions
**Value:** When large issues are detected, TPM suggests breakdown into Gate 1-focused subtasks.
**Acceptance Criteria:** TPM comments with proposed task decomposition + rationale.
**Complexity:** L
**Dependencies:** F1 (alignment scoring)

#### F7: Historical Trend Analysis
**Value:** Track alignment drift over time (are we staying focused on Gate 1?).
**Acceptance Criteria:** Chart showing alignment score trend, posted weekly.
**Complexity:** M
**Dependencies:** F1 (requires historical scoring data)

#### F8: Custom Trigger Support
**Value:** Run TPM on-demand via slash command or GitHub comment (`/tpm analyze`).
**Acceptance Criteria:** Triggerable via comment on any issue/PR.
**Complexity:** M
**Dependencies:** None (wraps existing automation)

---

## Next Steps

1. **Review feature ideas** with stakeholder(s)
2. **Prioritize features** based on value vs. complexity
3. **Sequence features** by dependency graph
4. **Define first increment** (likely F1 or F3)
5. **Ship, test, iterate**

---

**Roadmap Status:** Draft (2025-11-15)
**Owner:** TPM Automation Working Group
**Stakeholders:** TBD
