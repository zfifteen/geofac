package com.geofac;

import com.geofac.util.DirichletKernel;
import com.geofac.util.SnapKernel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.IntStream;

import ch.obermuhlner.math.big.BigDecimalMath;

/**
 * Geometric Resonance Factorization Service
 *
 * Implements platform-independent factorization using:
 * - Dirichlet kernel filtering
 * - Golden-ratio QMC sampling
 * - High-precision BigDecimal arithmetic
 *
 * Ported from: z-sandbox GeometricResonanceFactorizer
 */
@Service
public class FactorizerService {

    private static final Logger log = LoggerFactory.getLogger(FactorizerService.class);

    @Value("${geofac.precision}")
    private int precision;

    @Value("${geofac.samples}")
    private long samples;

    @Value("${geofac.m-span}")
    private int mSpan;

    @Value("${geofac.j}")
    private int J;

    @Value("${geofac.threshold}")
    private double threshold;

    @Value("${geofac.k-lo}")
    private double kLo;

    @Value("${geofac.k-hi}")
    private double kHi;

    @Value("${geofac.search-timeout-ms:15000}")
    private long searchTimeoutMs;

    private static final SecureRandom RANDOM = new SecureRandom();
    private static final BigInteger TWO = BigInteger.valueOf(2L);
    private static final int[] SMALL_PRIMES = {
        3, 5, 7, 11, 13, 17, 19, 23, 29, 31,
        37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
        79, 83, 89, 97, 101, 103, 107, 109, 113, 127,
        131, 137, 139, 149, 151, 157, 163, 167, 173, 179,
        181, 191, 193, 197, 199, 211, 223, 227, 229
    };

    /**
     * Factor a semiprime N into p × q
     *
     * @param N The number to factor
     * @return Array [p, q] if successful, null if not found
     * @throws IllegalArgumentException if N is invalid
     */
    public BigInteger[] factor(BigInteger N) {
        // Validation
        if (N == null) {
            throw new IllegalArgumentException("N cannot be null");
        }
        if (N.signum() <= 0) {
            throw new IllegalArgumentException("N must be positive");
        }
        if (N.compareTo(BigInteger.TEN) < 0) {
            throw new IllegalArgumentException("N must be at least 10");
        }

        log.info("=== Geometric Resonance Factorization ===");
        log.info("N = {} ({} bits)", N, N.bitLength());

        // Adaptive precision based on bit length
        int adaptivePrecision = Math.max(precision, N.bitLength() * 2 + 100);
        MathContext mc = new MathContext(adaptivePrecision, RoundingMode.HALF_EVEN);

        log.info("Precision: {} decimal digits", adaptivePrecision);
        log.info("Configuration: samples={}, m-span={}, J={}, threshold={}",
                 samples, mSpan, J, threshold);

        // Initialize constants
        BigDecimal bdN = new BigDecimal(N, mc);
        BigDecimal lnN = BigDecimalMath.log(bdN, mc);
        BigDecimal pi = BigDecimalMath.pi(mc);
        BigDecimal twoPi = pi.multiply(BigDecimal.valueOf(2), mc);
        BigDecimal phiInv = computePhiInv(mc);

        log.info("Starting search...");
        long startTime = System.currentTimeMillis();

        // Search
        BigInteger[] result = search(N, mc, lnN, twoPi, phiInv, startTime);

        long duration = System.currentTimeMillis() - startTime;
        log.info("Search completed in {}.{} seconds", duration / 1000, duration % 1000);

        if (result == null) {
            log.warn("Geometric search exhausted without locating factors; switching to Pollard Rho fallback");
            result = pollardRhoFactorization(N);
        }

        if (result != null) {
            log.info("=== SUCCESS ===");
            log.info("p = {}", result[0]);
            log.info("q = {}", result[1]);

            // Verify
            if (!result[0].multiply(result[1]).equals(N)) {
                log.error("VERIFICATION FAILED: p × q ≠ N");
                throw new IllegalStateException("Product check failed");
            }
            log.info("Verification: p × q = N ✓");
        } else {
            log.error("All factorization strategies failed for {}", N);
            log.warn("Consider: increase samples, m-span, or adjust threshold");
        }

        return result;
    }

    private BigInteger[] search(BigInteger N, MathContext mc, BigDecimal lnN,
                                BigDecimal twoPi, BigDecimal phiInv, long startTime) {
        BigDecimal u = BigDecimal.ZERO;
        BigDecimal kWidth = BigDecimal.valueOf(kHi - kLo);
        BigDecimal thresholdBd = BigDecimal.valueOf(threshold);

        int progressInterval = (int) Math.max(1, samples / 10); // Log every 10%

        for (long n = 0; n < samples; n++) {
            if (searchTimeoutMs > 0 && System.currentTimeMillis() - startTime >= searchTimeoutMs) {
                log.warn("Geometric search timed out after {} samples (configured {} ms)", n, searchTimeoutMs);
                return null;
            }

            if (n > 0 && n % progressInterval == 0) {
                int percent = (int) ((n * 100) / samples);
                log.info("Progress: {}% ({}/{})", percent, n, samples);
            }

            // Update golden ratio sequence
            u = u.add(phiInv, mc);
            if (u.compareTo(BigDecimal.ONE) >= 0) {
                u = u.subtract(BigDecimal.ONE, mc);
            }

            BigDecimal k = BigDecimal.valueOf(kLo).add(kWidth.multiply(u, mc), mc);
            BigInteger m0 = BigInteger.ZERO; // Balanced semiprime assumption

            AtomicReference<BigInteger[]> result = new AtomicReference<>();

            // Parallel m-scan
            IntStream.rangeClosed(-mSpan, mSpan).parallel().forEach(dm -> {
                if (result.get() != null) return; // Early exit if found

                BigInteger m = m0.add(BigInteger.valueOf(dm));
                BigDecimal theta = twoPi.multiply(new BigDecimal(m), mc).divide(k, mc);

                // Dirichlet kernel filtering
                BigDecimal amplitude = DirichletKernel.normalizedAmplitude(theta, J, mc);
                if (amplitude.compareTo(thresholdBd) > 0) {
                    BigInteger p0 = SnapKernel.phaseCorrectedSnap(lnN, theta, mc);

                    // Test candidate and neighbors
                    BigInteger[] hit = testNeighbors(N, p0);
                    if (hit != null) {
                        result.compareAndSet(null, hit);
                    }
                }
            });

            if (result.get() != null) {
                log.info("Factor found at k-sample {}/{}", n + 1, samples);
                return result.get();
            }
        }

        return null;
    }

    private BigInteger[] testNeighbors(BigInteger N, BigInteger pCenter) {
        // Test p, p-1, p+1
        BigInteger[] offsets = { BigInteger.ZERO, BigInteger.valueOf(-1), BigInteger.ONE };
        for (BigInteger off : offsets) {
            BigInteger p = pCenter.add(off);
            if (p.compareTo(BigInteger.ONE) <= 0 || p.compareTo(N) >= 0) {
                continue;
            }
            if (N.mod(p).equals(BigInteger.ZERO)) {
                BigInteger q = N.divide(p);
                return ordered(p, q);
            }
        }
        return null;
    }

    private static BigInteger[] ordered(BigInteger a, BigInteger b) {
        return (a.compareTo(b) <= 0) ? new BigInteger[]{a, b} : new BigInteger[]{b, a};
    }

    private BigDecimal computePhiInv(MathContext mc) {
        // φ⁻¹ = (√5 - 1) / 2
        BigDecimal sqrt5 = BigDecimalMath.sqrt(BigDecimal.valueOf(5), mc);
        return sqrt5.subtract(BigDecimal.ONE, mc).divide(BigDecimal.valueOf(2), mc);
    }

    // Package-private getters for testing
    long getSamples() {
        return samples;
    }

    int getMSpan() {
        return mSpan;
    }

    private BigInteger[] pollardRhoFactorization(BigInteger n) {
        if (n == null || n.compareTo(BigInteger.ONE) <= 0) {
            return null;
        }

        if (n.remainder(TWO).equals(BigInteger.ZERO)) {
            return ordered(TWO, n.divide(TWO));
        }

        List<BigInteger> primes = new ArrayList<>(2);
        factorRecursively(n, primes);
        if (primes.size() >= 2) {
            return ordered(primes.get(0), primes.get(1));
        }
        return null;
    }

    private void factorRecursively(BigInteger n, List<BigInteger> factors) {
        if (n.compareTo(BigInteger.ONE) <= 0 || factors.size() >= 2) {
            return;
        }

        BigInteger small = trialDivision(n);
        if (small != null && !small.equals(BigInteger.ONE) && !small.equals(n)) {
            factorRecursively(small, factors);
            factorRecursively(n.divide(small), factors);
            return;
        }

        if (n.isProbablePrime(40)) {
            factors.add(n);
            return;
        }

        BigInteger divisor = pollardRhoInternal(n);
        if (divisor == null || divisor.equals(n)) {
            return;
        }

        factorRecursively(divisor, factors);
        factorRecursively(n.divide(divisor), factors);
    }

    private BigInteger trialDivision(BigInteger n) {
        if (n.remainder(TWO).equals(BigInteger.ZERO)) {
            return TWO;
        }

        for (int prime : SMALL_PRIMES) {
            BigInteger candidate = BigInteger.valueOf(prime);
            if (n.remainder(candidate).equals(BigInteger.ZERO)) {
                return candidate;
            }
        }
        return null;
    }

    private BigInteger pollardRhoInternal(BigInteger n) {
        if (n.mod(TWO).equals(BigInteger.ZERO)) {
            return TWO;
        }

        while (true) {
            BigInteger c = randomBetween(BigInteger.ONE, n.subtract(BigInteger.ONE));
            BigInteger x = randomBetween(TWO, n.subtract(BigInteger.ONE));
            BigInteger y = x;
            BigInteger d = BigInteger.ONE;

            while (d.equals(BigInteger.ONE)) {
                x = iterateRho(x, c, n);
                y = iterateRho(iterateRho(y, c, n), c, n);
                d = x.subtract(y).abs().gcd(n);
                if (d.equals(n)) {
                    break;
                }
            }

            if (d.compareTo(BigInteger.ONE) > 0 && d.compareTo(n) < 0) {
                return d;
            }
        }
    }

    private BigInteger iterateRho(BigInteger x, BigInteger c, BigInteger mod) {
        return x.multiply(x).add(c).mod(mod);
    }

    private BigInteger randomBetween(BigInteger minInclusive, BigInteger maxInclusive) {
        BigInteger range = maxInclusive.subtract(minInclusive).add(BigInteger.ONE);
        BigInteger candidate;
        do {
            candidate = new BigInteger(range.bitLength(), RANDOM);
        } while (candidate.compareTo(range) >= 0);
        return candidate.add(minInclusive);
    }
}
