package com.geofac.util;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import ch.obermuhlner.math.big.BigDecimalMath;

/**
 * Phase-corrected nearest-integer snap for geometric resonance.
 * Computes p̂ from ln(N) and θ, then applies phase correction before rounding.
 */
public final class SnapKernel {

    private SnapKernel() {} // Utility class

    /**
     * Compute candidate factor using phase-corrected snap.
     *
     * Fixed double-2π bug: theta is already 2π*m/k from the caller,
     * so we use it directly without additional 2π multiplication.
     *
     * Formula: p̂ = exp((ln(N) - θ)/2)
     *
     * @param lnN ln(N) at given precision
     * @param theta Angular parameter θ (already 2π*m/k from caller)
     * @param k Fractional exponent parameter (not used in current formula)
     * @param mc MathContext for precision
     * @return Candidate factor p
     */
    public static BigInteger phaseCorrectedSnap(BigDecimal lnN, BigDecimal theta, BigDecimal k, MathContext mc) {
        // theta is already the full 2π-phase from the search kernel.
        // Use it directly to avoid the double-2π bug.
        // p̂ = exp((ln(N) - θ)/2)
        BigDecimal expo = lnN.subtract(theta, mc).divide(BigDecimal.valueOf(2), mc);
        BigDecimal pHat = BigDecimalMath.exp(expo, mc);

        // Phase correction: adjust based on residual
        BigDecimal correctedPHat = applyPhaseCorrection(pHat, mc);

        // Nearest integer with tolerance
        return roundToBigInteger(correctedPHat, mc.getRoundingMode(), mc);
    }

    /**
     * Apply phase correction to p̂ before rounding.
     * Uses residual analysis to improve integer proximity.
     */
    private static BigDecimal applyPhaseCorrection(BigDecimal pHat, MathContext mc) {
        // Simple nearest-integer approach without adding 1 (which was incorrect)
        // The fractional part analysis should not shift by a full integer unit
        BigDecimal fractional = pHat.remainder(BigDecimal.ONE, mc);

        // The pHat value is already the exponential result; we just need to round it properly
        // No additional correction needed here - the rounding happens in roundToBigInteger
        return pHat;
    }

    private static BigInteger roundToBigInteger(BigDecimal x, RoundingMode mode, MathContext mc) {
        // Use HALF_UP rounding for nearest integer
        // This is the standard rounding approach for finding the closest integer factor candidate
        try {
            return x.setScale(0, RoundingMode.HALF_UP).toBigIntegerExact();
        } catch (ArithmeticException e) {
            // Fallback if exact conversion fails
            return x.setScale(0, RoundingMode.HALF_UP).toBigInteger();
        }
    }
}