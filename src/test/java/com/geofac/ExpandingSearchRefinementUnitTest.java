package com.geofac;

import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for expandingSearchRefinement to verify it finds factors
 * at non-boundary offsets (not just at exact radius values).
 * 
 * This addresses the critical issue identified in PR review where the
 * original implementation only checked boundary points (±10, ±100, etc.)
 * and would miss factors at intermediate offsets like ±11 or ±5000.
 */
public class ExpandingSearchRefinementUnitTest {

    /**
     * Test that the refinement finds factors at non-boundary offsets.
     * Uses reflection to access the private method for unit testing.
     */
    @Test
    void testNonBoundaryOffset() throws Exception {
        // Use the example from the PR comment:
        // N = 3162277 × 3162319 = 10000128640363
        BigInteger p = new BigInteger("3162277");
        BigInteger q = new BigInteger("3162319");
        BigInteger N = p.multiply(q);
        
        // Create a service instance
        FactorizerService service = new FactorizerService();
        
        // Use reflection to access the private method
        Method method = FactorizerService.class.getDeclaredMethod(
            "expandingSearchRefinement", BigInteger.class, BigInteger.class);
        method.setAccessible(true);
        
        // Test with offset=11 (not a boundary value)
        // This simulates a geometric resonance candidate that's 11 units away from the true factor
        BigInteger p0_offset11 = p.add(BigInteger.valueOf(11));
        BigInteger[] result = (BigInteger[]) method.invoke(service, p0_offset11, N);
        
        assertNotNull(result, "Should find factors at offset=11 (non-boundary)");
        assertEquals(N, result[0].multiply(result[1]), "Product should equal N");
        assertTrue((result[0].equals(p) && result[1].equals(q)) || 
                   (result[0].equals(q) && result[1].equals(p)),
                   "Should find the correct factors");
        
        // Test with offset=10 (boundary value, should still work)
        BigInteger p0_offset10 = p.add(BigInteger.valueOf(10));
        result = (BigInteger[]) method.invoke(service, p0_offset10, N);
        
        assertNotNull(result, "Should find factors at offset=10 (boundary)");
        assertEquals(N, result[0].multiply(result[1]), "Product should equal N");
        
        // Test with offset=5000 (intermediate value in 1K-10K ring)
        BigInteger p0_offset5000 = p.add(BigInteger.valueOf(5000));
        result = (BigInteger[]) method.invoke(service, p0_offset5000, N);
        
        assertNotNull(result, "Should find factors at offset=5000 (intermediate)");
        assertEquals(N, result[0].multiply(result[1]), "Product should equal N");
        
        // Test with p0 exactly equal to p (offset=0)
        result = (BigInteger[]) method.invoke(service, p, N);
        
        assertNotNull(result, "Should find factors when p0 is exact");
        assertEquals(N, result[0].multiply(result[1]), "Product should equal N");
    }

    /**
     * Test that the refinement works in both directions (+ and - offsets).
     */
    @Test
    void testBothDirections() throws Exception {
        BigInteger p = new BigInteger("3162277");
        BigInteger q = new BigInteger("3162319");
        BigInteger N = p.multiply(q);
        
        FactorizerService service = new FactorizerService();
        Method method = FactorizerService.class.getDeclaredMethod(
            "expandingSearchRefinement", BigInteger.class, BigInteger.class);
        method.setAccessible(true);
        
        // Test with positive offset (p0 > p)
        BigInteger p0_positive = p.add(BigInteger.valueOf(25));
        BigInteger[] result = (BigInteger[]) method.invoke(service, p0_positive, N);
        
        assertNotNull(result, "Should find factors with positive offset");
        assertEquals(N, result[0].multiply(result[1]), "Product should equal N");
        
        // Test with negative offset (p0 < p)
        BigInteger p0_negative = p.subtract(BigInteger.valueOf(25));
        result = (BigInteger[]) method.invoke(service, p0_negative, N);
        
        assertNotNull(result, "Should find factors with negative offset");
        assertEquals(N, result[0].multiply(result[1]), "Product should equal N");
    }

    /**
     * Test that method returns null when no factor is found within search budget.
     */
    @Test
    void testNoFactorFound() throws Exception {
        // Use a prime number as N (no non-trivial factors)
        BigInteger N = new BigInteger("10000000000000061"); // Large prime in Gate 2 range
        BigInteger p0 = new BigInteger("3162277777"); // Random starting point
        
        FactorizerService service = new FactorizerService();
        Method method = FactorizerService.class.getDeclaredMethod(
            "expandingSearchRefinement", BigInteger.class, BigInteger.class);
        method.setAccessible(true);
        
        BigInteger[] result = (BigInteger[]) method.invoke(service, p0, N);
        
        assertNull(result, "Should return null when no factor found within search budget");
    }
}
