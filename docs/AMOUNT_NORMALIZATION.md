# Amount Sign Normalization

## Credit Card Sign Conventions

Different credit card providers use different conventions for representing transaction amounts:

### Original Formats

- **Apple Card**:
  - Positive = Expenses (money you spent)
  - Negative = Refunds (money back to you)

- **Bilt Card**: 
  - Negative = Expenses (money you spent)
  - Positive = Payments/Refunds (money paid to card)

- **Chase Cards** (Sapphire, Freedom):
  - Negative = Expenses (money you spent)
  - Positive = Refunds (money back to you)

### Normalized Format

The concatenation script automatically normalizes all transactions to follow Apple's convention:

- **Positive amounts** = Expenses (money going out)
- **Negative amounts** = Refunds/Payments (money coming in)

This normalization happens automatically in `scripts/concatenate_transactions.py`:
- Apple transactions: kept as-is (already follow standard)
- Bilt transactions: signs are flipped (`amount = -amount`)
- Chase transactions: signs are flipped (`amount = -amount`)

## Why This Matters

This normalization ensures:
1. Consistent expense tracking across all cards
2. Accurate total expense calculations
3. Proper categorization of refunds vs expenses
4. Dashboard charts and summaries work correctly
5. Intuitive positive/negative representation (expenses are positive)

## Implementation

See the `load_chase_file()` and `load_apple_file()` functions in `scripts/concatenate_transactions.py` for the normalization logic.

