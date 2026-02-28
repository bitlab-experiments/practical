/**
 * Node.js script to calculate expected values of smallest and largest numbers
 * in a 49/6 lottery draw
 */

// Function to calculate factorial
function factorial(n) {
  if (n < 0) return undefined;
  if (n === 0 || n === 1) return 1;
  let result = 1;
  for (let i = 2; i <= n; i++) {
    result *= i;
  }
  return result;
}

// Function to calculate combinations C(n, k) = n! / (k! * (n-k)!)
function combination(n, k) {
  if (k > n || k < 0) return 0;
  if (k === 0 || k === n) return 1;
  
  // Optimize by using C(n, k) = C(n, n-k)
  if (k > n - k) {
    k = n - k;
  }
  
  let result = 1;
  for (let i = 0; i < k; i++) {
    result *= (n - i);
    result /= (i + 1);
  }
  return Math.round(result);
}

// Lottery parameters
const n = 49;  // total numbers
const k = 6;   // numbers drawn

// Total combinations for the lottery
const totalCombinations = combination(n, k);
console.log(`\n${'='.repeat(80)}`);
console.log('EXPECTED VALUE CALCULATOR FOR 49/6 LOTTERY');
console.log(`${'='.repeat(80)}\n`);

console.log(`Total combinations C(${n},${k}) = ${totalCombinations.toLocaleString()}\n`);

// ============================================================================
// Calculate Expected Value of SMALLEST Number
// ============================================================================
console.log(`${'─'.repeat(80)}`);
console.log('EXPECTED VALUE OF SMALLEST NUMBER');
console.log(`${'─'.repeat(80)}\n`);

let expectedSmallest = 0;
let smallestData = [];

console.log('i    C(49-i,5)        Probability          i × P(X_(1)=i)      ');
console.log(`${'-'.repeat(80)}`);

for (let i = 1; i <= n - k + 1; i++) {
  // If smallest is i, remaining k-1 numbers chosen from {i+1, ..., n}
  const combos = combination(n - i, k - 1);
  const prob = combos / totalCombinations;
  const contribution = i * prob;
  
  smallestData.push({ i, combos, prob, contribution });
  expectedSmallest += contribution;
  
  // Print selected rows (first 10, last 5, and every 5th in between)
  if (i <= 10 || i > n - k - 4 || i % 5 === 0) {
    const row = `${String(i).padEnd(4)} ${combos.toLocaleString().padEnd(15)} ${prob.toFixed(10).padEnd(18)} ${contribution.toFixed(10).padEnd(18)}`;
    console.log(row);
  } else if (i === 11) {
    const dots = `${'...'.padEnd(4)} ${'...'.padEnd(15)} ${'...'.padEnd(18)} ${'...'.padEnd(18)}`;
    console.log(dots);
  }
}

console.log(`${'-'.repeat(80)}`);
console.log(`Sum of all contributions = ${expectedSmallest.toFixed(10)}`);
console.log(`\n✓ Expected value E[X_(1)] ≈ ${expectedSmallest.toFixed(2)}\n`);

// ============================================================================
// Calculate Expected Value of LARGEST Number
// ============================================================================
console.log(`${'─'.repeat(80)}`);
console.log('EXPECTED VALUE OF LARGEST NUMBER');
console.log(`${'─'.repeat(80)}\n`);

let expectedLargest = 0;
let largestData = [];

console.log('i    C(i-1,5)         Probability          i × P(X_(k)=i)      ');
console.log(`${'-'.repeat(80)}`);

for (let i = k; i <= n; i++) {
  // If largest is i, remaining k-1 numbers chosen from {1, ..., i-1}
  const combos = combination(i - 1, k - 1);
  const prob = combos / totalCombinations;
  const contribution = i * prob;
  
  largestData.push({ i, combos, prob, contribution });
  expectedLargest += contribution;
  
  // Print selected rows (first 10, last 5, and every 5th in between)
  if (i <= k + 9 || i > n - 4 || i % 5 === 0) {
    const row = `${String(i).padEnd(4)} ${combos.toLocaleString().padEnd(15)} ${prob.toFixed(10).padEnd(18)} ${contribution.toFixed(10).padEnd(18)}`;
    console.log(row);
  } else if (i === k + 10) {
    const dots = `${'...'.padEnd(4)} ${'...'.padEnd(15)} ${'...'.padEnd(18)} ${'...'.padEnd(18)}`;
    console.log(dots);
  }
}

console.log(`${'-'.repeat(80)}`);
console.log(`Sum of all contributions = ${expectedLargest.toFixed(10)}`);
console.log(`\n✓ Expected value E[X_(k)] ≈ ${expectedLargest.toFixed(2)}\n`);

// ============================================================================
// Summary
// ============================================================================
console.log(`${'='.repeat(80)}`);
console.log('SUMMARY');
console.log(`${'='.repeat(80)}\n`);

console.log(`Expected value of smallest number: ${expectedSmallest.toFixed(4)}`);
console.log(`Expected value of largest number:  ${expectedLargest.toFixed(4)}\n`);

// Additional statistics
const smallestRange1to7 = smallestData
  .filter(d => d.i >= 1 && d.i <= 7)
  .reduce((sum, d) => sum + d.prob, 0);

const largestRange43to49 = largestData
  .filter(d => d.i >= 43 && d.i <= 49)
  .reduce((sum, d) => sum + d.prob, 0);

console.log(`Probability smallest number is in range [1-7]:   ${(smallestRange1to7 * 100).toFixed(2)}%`);
console.log(`Probability largest number is in range [43-49]:  ${(largestRange43to49 * 100).toFixed(2)}%\n`);

console.log(`${'='.repeat(80)}\n`);
