# Checklist: Constitutional Alignment for Fallback Removal

**Purpose**: A final self-check to ensure the planned refactoring strictly adheres to the project constitution before implementation begins.
**Focus**: Alignment with "Resonance-Only" (Principle I) and "Test-First Development" (Principle IV).
**Scope**: Changes to `FactorizerService` and the new `NoFallbackTest`.
**Created**: 2025-11-12

---

## Constitutional Alignment (Principle I: Resonance-Only)

- [ ] CHK001 - Does the spec explicitly require the *complete removal* of the Pollard's Rho code path? [Clarity, Spec §2.1]
- [ ] CHK002 - Are the requirements for reporting a clear failure (instead of falling back) unambiguously defined? [Clarity, Spec §2.2]
- [ ] CHK003 - Is the requirement to delete the `pollardsRhoWithDeadline` method and its helpers explicitly stated? [Completeness, Spec §2.3]
- [ ] CHK004 - Do the acceptance criteria confirm that no fallback method is attempted upon resonance search failure? [Measurability, Spec §5]
- [ ] CHK005 - Have all potential entry points to the old fallback logic been identified and slated for removal in the tasks? [Coverage, tasks.md]

## Test-First Development (Principle IV)

- [ ] CHK006 - Does the spec's acceptance criteria mandate a new test for the fallback removal? [Clarity, Spec §5]
- [ ] CHK007 - Is the requirement for this new test to fail *before* implementation and pass *after* explicitly documented in the tasks? [Measurability, tasks.md]
- [ ] CHK008 - Are the requirements for the new test scenario (i.e., forcing a resonance failure) clearly defined? [Clarity, tasks.md T002]
- [ ] CHK009 - Do the tasks place the creation of the new test file and method *before* the implementation tasks? [Consistency, tasks.md]

## Non-Functional Requirements

- [ ] CHK010 - Is the performance requirement (no statistically significant regression) clearly stated and measurable? [Clarity, Spec §3]
- [ ] CHK011 - Is there a specific task defined to verify the performance requirement? [Completeness, tasks.md T008]
- [ ] CHK012 - Are the requirements for code clarity and improved control flow documented in the spec? [Completeness, Spec §3]

## General Requirements Quality

- [ ] CHK013 - Are all functional and non-functional requirements in the spec covered by at least one task in `tasks.md`? [Coverage]
- [ ] CHK014 - Is the scope of the change clearly defined, with out-of-scope items explicitly listed? [Clarity, Spec §4]
- [ ] CHK015 - Have all ambiguities identified during the `/speckit.clarify` session been resolved and integrated into the spec? [Consistency, Spec §Clarifications]
