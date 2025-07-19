# LLM inference GPU memory requirement

## Formula

### 1. General

$$
M = m + a + k + o
$$

Where:

- $M$ : Total memory required (in bytes).

- $m$ : Memory for Model Parameters.

- $a$: Memory for intermediate activations during forward passes.

- $k$: Memory for the key-value cache used in autoregressive generation.

- $o$: Memory for framework overheads (e.g., PyTorch buffers, temporary tensors) and system processes.

### 2. Memory for Model Parameters ($m$)

Since each Large Language Model (LLM) has a different number of parameters and may use different numerical precisions, they require varying GPU capabilities for inference and fine-tuning.

Total memory required for model parameters is defined by formula:

$$
m = \dfrac{pt}{8 \ (bytes)}
$$

where:

- $p$ : Number of parameters e.g. 7B, 32B etc.

- $t$ : Tensor type or precision bits e.g. 16 bits (BF16).

### 2. Memory for Activations ($a$)
Activations are the intermediate outputs of each layer during the forward pass.

A rough estimate for activations per layer is:

$$
a_{per \_ layer} ≈ \frac{bsht}{8 \ bytes}
$$

For the entire model (assuming activations are stored for all layers, though some frameworks reuse memory):

$$
a ≈ \frac{lbsht}{8 \ bytes}
$$

where:
- **Batch size ($b$)**: Number of input sequences processed simultaneously.
- **Sequence length ($s$)**: Number of tokens in the input/output (context length).
- **Hidden size ($h$)**: The model’s hidden dimension (e.g., 4096 for many 7B models like LLaMA).
- **Number of layers ($l$)**: Number of transformer layers (e.g., 32 for LLaMA-based 7B models).
- **Precision ($t$)**: Bits per parameter (16 for BF16/FP16).

**Example for  Llama 2 7B:**
- LLaMA-like architecture:
    - $l$ = 32 layers,
    - $h$ = 4096 (hidden size).

- Typical inference:
    - $b$ = 1 (single sequence),
    - $s$ = 512 tokens (moderate context length),
    - $t$ = 16 bits.

Result:

  - $a_{per \_ layer} = \dfrac{1 \cdot 512 \cdot 4096 \cdot 16}{8} = 4,194,304 \ bytes ≈ 4.2 MB$

  - $a = 32 \times 4.2 \ MB ≈ 134.4 \ MB$


For a longer context (e.g. $s = 2048$):

  - $a_{per \_ layer} = \dfrac{1 \cdot 2048 \cdot 4096 \cdot 16}{8} ≈ 134.2 \ MB$

  - $a = 32 \times 134.2 \ MB ≈ 4.3 \ GB$

### 3. Memory for KV Cache ($k$)

The KV cache stores key and value tensors for attention mechanisms during autoregressive generation.

It stores keys and values for each token, layer, and head as defined as:

$$
k ≈ \dfrac{b \cdot s \cdot l \cdot h \cdot 2 \cdot t}{8 \ bytes}
$$

(The factor of 2 accounts for both keys and values.)

where: 

- $b$: Batch size.
- $s$: Sequence length (including input and generated tokens).
- $h$: Hidden size.
- $l$: Number of layers.
- $t$: Precision.

**Example for Lingshu-7B:**

Assume
- $l = 32$,
- $h = 4096$,
- $b = 1$, 
- $s = 512$,
- $t = 16$.

Result:

$k = \dfrac{1 \cdot 512 \cdot 32 \cdot 4096 \cdot 2 \cdot 16}{8} ≈ 268,435,456 \ bytes ≈ 268.44 \ MB$

For $s = 2048$:

$k = \dfrac{1 \cdot 2048 \cdot 32 \cdot 4096 \cdot 2 \cdot 16}{8} ≈ 1,073,741,824 \ bytes \approx 1.1 \ GB$

### 4. Memory for Overheads ($o$)

Framework and system overheads include:

- **PyTorch/Tensor buffers**: Temporary tensors for matrix operations or gradient computations.
macOS processes: On your Mac M1, unified memory is shared with the OS and other apps (~2–4 GB for macOS and background processes).

- **MPS backend inefficiencies**: Apple’s Metal API (used by PyTorch’s MPS backend) may have higher memory overhead than CUDA.

A rough estimate for overheads:

- **Framework overhead**: ~1–2 GB for PyTorch or Hugging Face’s transformers.
- **macOS usage**: ~2–4 GB for system processes (check Activity Monitor).

**Conservative estimate**: o ≈ 3–5 GB (framework + macOS).

### 5. Full equation

We have:

$M = m + a + k + o$

$\implies M = \dfrac{pt + lbsht + 2lbsht}{8} + o$

$\implies M = \dfrac{t (p + lbsh + 2bslh)}{8} + o$

$\implies M = \dfrac{t(p + 3lbsh)}{8} + o$

For Linux/Windows (separate memory):

$$
M = \frac{t(p + 3lbsh)}{8} + 2,000,000,000
$$

For Mac (Unified memory):

$$
M = \frac{t(p + 3lbsh)}{8} + 5,000,000,000
$$

## Example

For  Llama 2 7B on Mac using Hugging Face's transformers:
- $p$ = 7,000,000,000 parameters.

- LLaMA-like architecture:
    - $l$ = 32 layers,
    - $h$ = 4096 (hidden size).

- Typical inference:
    - $b$ = 1 (single sequence),
    - $s$ = 512 tokens (moderate context length),
    - $t$ = 16 bits.

- $o$ = 5,000,000,000.

Result:

$M = m + a + k + o$

$\implies M = \dfrac{t(p + 3lbsh)}{8} + 5,000,000,000$

$\implies M = \dfrac{16(7,000,000,000 + 3(32 \cdot 1 \cdot 512 \cdot 4096))}{8} + 5,000,000,000$

$\implies M = \dfrac{115,221,225,472}{8} + 5,000,000,000$

$\implies M = 14,402,653,184 + 5,000,000,000 = 19,402,653,184 \ bytes$

$\implies M  \approx 19.41 \ GB \approx 18.07 \ GiB$