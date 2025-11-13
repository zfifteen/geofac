# Implementation Plan: Remove Pollard's Rho Fallback

**Branch**: `001-remove-fallback` | **Date**: 2025-11-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-remove-fallback/spec.md`

## Summary

This plan details the refactoring of `FactorizerService` to remove the Pollard's Rho fallback mechanism. The change ensures the system adheres to the "Resonance-Only" principle and provides clear, unambiguous failure states, aligning with the project constitution.

## Technical Context

**Language/Version**: Java 17+
**Primary Dependencies**: Spring Boot 3.2.0, ch.obermuhlner:big-math
**Storage**: N/A
**Testing**: JUnit 5 with Spring Boot Test
**Target Platform**: JVM
**Project Type**: Single project
**Performance Goals**: Run existing benchmarks and ensure no statistically significant regression.
**Constraints**: N/A
**Scale/Scope**: N/A

## Constitution Check

*This refactoring aligns with all constitutional principles, particularly "Resonance-Only Factorization" (I) and "Test-First Development" (IV).*

## Project Structure

### Documentation (this feature)

```text
specs/001-remove-fallback/
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)
```text
src/
└── main/
    └── java/
        └── com/
            └── geofac/
                ├── FactorizerService.java  # Target of modification
                └── ...
└── test/
    └── java/
        └── com/
            └── geofac/
                ├── NoFallbackTest.java     # New test file
                └── ...
```

**Structure Decision**: The project uses a standard single-project structure. The changes are localized to the `com.geofac` package.

## Complexity Tracking

No constitutional violations are required for this feature.
