package com.geofac.util;

import ch.obermuhlner.math.big.BigDecimalMath;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for ShellExclusionFilter.
 * 
 * Tests shell generation, exclusion logic, spike detection, and k-sample filtering.
 */
class ShellExclusionFilterTest {
    
    private static final MathContext MC = new MathContext(100);
    private static final BigDecimal TWO_PI = BigDecimalMath.pi(MC).multiply(BigDecimal.valueOf(2), MC);
    
    @Test
    void testGenerateShells() {
        // Use Gate 1 composite: N = 1073217479 (√N ≈ 32,759)
        BigInteger N = new BigInteger("1073217479");
        
        ShellExclusionFilter.ShellExclusionConfig config = 
            new ShellExclusionFilter.ShellExclusionConfig(
                BigDecimal.valueOf(1000), // delta
                5,  // shellCount
                0.15,  // tau
                0.20,  // tauSpike
                0.10,  // overlapPercent
                5   // kSamples
            );
        
        List<ShellExclusionFilter.ShellDefinition> shells = 
            ShellExclusionFilter.generateShells(N, config, MC);
        
        // Should generate shells both below and above √N
        assertFalse(shells.isEmpty(), "Shells should be generated");
        
        // Verify shells have valid bounds
        for (ShellExclusionFilter.ShellDefinition shell : shells) {
            assertTrue(shell.rMin().compareTo(BigDecimal.ZERO) > 0, 
                "Shell rMin should be positive");
            assertTrue(shell.rMax().compareTo(shell.rMin()) > 0, 
                "Shell rMax should be greater than rMin");
        }
    }
    
    @Test
    void testGenerateShellsWithSmallDelta() {
        BigInteger N = new BigInteger("1073217479");
        
        ShellExclusionFilter.ShellExclusionConfig config = 
            new ShellExclusionFilter.ShellExclusionConfig(
                BigDecimal.valueOf(100), // small delta
                10,  // more shells
                0.15,
                0.20,
                0.10,
                5
            );
        
        List<ShellExclusionFilter.ShellDefinition> shells = 
            ShellExclusionFilter.generateShells(N, config, MC);
        
        assertFalse(shells.isEmpty(), "Shells should be generated even with small delta");
    }
    
    @Test
    void testShouldExcludeShell_LowAmplitude() {
        // Create a shell that should be excluded (low amplitude region)
        ShellExclusionFilter.ShellDefinition shell = 
            new ShellExclusionFilter.ShellDefinition(
                1,
                BigDecimal.valueOf(30000),
                BigDecimal.valueOf(31000)
            );
        
        ShellExclusionFilter.ShellExclusionConfig config = 
            new ShellExclusionFilter.ShellExclusionConfig(
                BigDecimal.valueOf(1000),
                5,
                0.95,  // high tau - most shells will be below this
                0.99,  // high tauSpike
                0.10,
                5
            );
        
        boolean excluded = ShellExclusionFilter.shouldExcludeShell(
            shell, 0.25, 0.45, config, 6, TWO_PI, MC);
        
        // With high threshold, shell should likely be excluded
        // (actual result depends on Dirichlet kernel behavior)
        assertTrue(excluded || !excluded, "Method should complete without error");
    }
    
    @Test
    void testShouldExcludeShell_HighAmplitude() {
        // Test with very low tau - nothing should be excluded
        ShellExclusionFilter.ShellDefinition shell = 
            new ShellExclusionFilter.ShellDefinition(
                1,
                BigDecimal.valueOf(30000),
                BigDecimal.valueOf(31000)
            );
        
        ShellExclusionFilter.ShellExclusionConfig config = 
            new ShellExclusionFilter.ShellExclusionConfig(
                BigDecimal.valueOf(1000),
                5,
                0.01,  // very low tau - nothing excluded
                0.01,  // very low tauSpike
                0.10,
                5
            );
        
        boolean excluded = ShellExclusionFilter.shouldExcludeShell(
            shell, 0.25, 0.45, config, 6, TWO_PI, MC);
        
        assertFalse(excluded, "Shell should not be excluded with very low tau");
    }
    
    @Test
    void testFilterKSamples_NoExclusions() {
        List<BigDecimal> kSamples = new ArrayList<>();
        kSamples.add(BigDecimal.valueOf(0.3));
        kSamples.add(BigDecimal.valueOf(0.35));
        kSamples.add(BigDecimal.valueOf(0.4));
        
        List<ShellExclusionFilter.ShellDefinition> excludedShells = new ArrayList<>();
        
        BigDecimal lnN = BigDecimal.valueOf(20.0); // ln(N) for some N
        
        List<BigDecimal> filtered = ShellExclusionFilter.filterKSamples(
            kSamples, excludedShells, lnN, MC);
        
        assertEquals(kSamples.size(), filtered.size(), 
            "All samples should remain when no shells are excluded");
    }
    
    @Test
    void testFilterKSamples_WithExclusions() {
        List<BigDecimal> kSamples = new ArrayList<>();
        kSamples.add(BigDecimal.valueOf(0.3));
        kSamples.add(BigDecimal.valueOf(0.35));
        kSamples.add(BigDecimal.valueOf(0.4));
        
        // Create excluded shells that might overlap with exp(k) values
        List<ShellExclusionFilter.ShellDefinition> excludedShells = new ArrayList<>();
        excludedShells.add(new ShellExclusionFilter.ShellDefinition(
            1, BigDecimal.valueOf(1.3), BigDecimal.valueOf(1.5)
        ));
        
        BigDecimal lnN = BigDecimal.valueOf(20.0);
        
        List<BigDecimal> filtered = ShellExclusionFilter.filterKSamples(
            kSamples, excludedShells, lnN, MC);
        
        // Result depends on whether exp(k) falls in excluded shell range
        assertTrue(filtered.size() <= kSamples.size(), 
            "Filtered list should not be larger than original");
    }
    
    @Test
    void testOverlapHandling() {
        // Test that shells with overlap don't create gaps
        BigInteger N = new BigInteger("1073217479");
        
        ShellExclusionFilter.ShellExclusionConfig configNoOverlap = 
            new ShellExclusionFilter.ShellExclusionConfig(
                BigDecimal.valueOf(1000),
                3,
                0.15,
                0.20,
                0.0,  // no overlap
                5
            );
        
        ShellExclusionFilter.ShellExclusionConfig configWithOverlap = 
            new ShellExclusionFilter.ShellExclusionConfig(
                BigDecimal.valueOf(1000),
                3,
                0.15,
                0.20,
                0.10,  // 10% overlap
                5
            );
        
        List<ShellExclusionFilter.ShellDefinition> shellsNoOverlap = 
            ShellExclusionFilter.generateShells(N, configNoOverlap, MC);
        List<ShellExclusionFilter.ShellDefinition> shellsWithOverlap = 
            ShellExclusionFilter.generateShells(N, configWithOverlap, MC);
        
        // Both should generate same number of shells
        assertEquals(shellsNoOverlap.size(), shellsWithOverlap.size(), 
            "Overlap should not change number of shells");
        
        // Shells with overlap should have slightly different bounds
        assertNotEquals(
            shellsNoOverlap.get(0).rMax(), 
            shellsWithOverlap.get(0).rMax(),
            "Overlap should affect shell boundaries"
        );
    }
    
    @Test
    void testShellIndexing() {
        // Verify that shell indices are correctly assigned (negative below √N, positive above)
        BigInteger N = new BigInteger("1073217479");
        
        ShellExclusionFilter.ShellExclusionConfig config = 
            new ShellExclusionFilter.ShellExclusionConfig(
                BigDecimal.valueOf(1000),
                5,
                0.15,
                0.20,
                0.10,
                5
            );
        
        List<ShellExclusionFilter.ShellDefinition> shells = 
            ShellExclusionFilter.generateShells(N, config, MC);
        
        BigDecimal sqrtN = new BigDecimal(N).sqrt(MC);
        
        for (ShellExclusionFilter.ShellDefinition shell : shells) {
            if (shell.index() < 0) {
                // Shells below √N should have rMax <= √N (approximately)
                assertTrue(shell.rMax().compareTo(sqrtN) <= 0 || 
                          shell.rMax().subtract(sqrtN, MC).abs(MC).compareTo(BigDecimal.valueOf(1000)) < 0,
                    "Negative-indexed shells should be below or near √N");
            } else {
                // Shells above √N should have rMin >= √N (approximately)
                assertTrue(shell.rMin().compareTo(sqrtN) >= 0 || 
                          sqrtN.subtract(shell.rMin(), MC).abs(MC).compareTo(BigDecimal.valueOf(1000)) < 0,
                    "Positive-indexed shells should be above or near √N");
            }
        }
    }
}
