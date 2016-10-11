from subkeys import generate_subkeys, permutate_bits

from utils import *

# The text that we want to be encrypted
plaintext = '0000000100100011010001010110011110001001101010111100110111101111'
print('Plaintext: %s' % plaintext)

# Get the subkeys
subkeys = generate_subkeys(key, p_box_56, shift_amounts, p_box_48)

# We first perform an initial permutation on the plaintext 64 bits
initial_permutation = permutate_bits(plaintext, initial_permutation_box)

# We initialise these to be previous as when we hit the for loop, we will be on the first iteration
previous_left_side = initial_permutation[0:len(initial_permutation)/2] # L0
previous_right_side = initial_permutation[len(initial_permutation)/2:len(initial_permutation)] # R0

# We now go through 16 iterations using a function f which operates on two blocks -- a data block of 32 bits (Rn) and a key, Kn (subkey from earlier) of 48 bits -- to produce a block of 32 bits.
# For n going from 1 to 16 we calculate:
# L(n) = R(n-1)
# R(n) = L(n-1) XOR f( R(n-1), K(n) )
for i in range(0, 16):
    current_left_side = previous_right_side # L1

    # To calculate f, we first expand each block Rn-1 from 32 bits to 48 bits. This is done by using a selection table that repeats some of the bits in Rn-1.
    # We'll call the use of this selection table the function E. Thus E(Rn-1) has a 32 bit input block, and a 48 bit output block.
    expanded_bits = permutate_bits(previous_right_side, e_box)

    # Next in the f calculation, we XOR the expanded bits E(Rn-1) with the key Kn
    # The zfill method will pad the beginning of the output binary string with zeroes if the output ends up being too short e.g. 47 instead of 48 bits
    k1_xor_e = '{0:b}'.format(int(subkeys[i], 2) ^ int(expanded_bits, 2))
    k1_xor_e = k1_xor_e.zfill(48)

    # To this point we have expanded Rn-1 from 32 bits to 48 bits, using the selection table, and XORed the result with the key Kn.
    # We now split the 48 bit string into 8 groups of 6 bits
    chunks = [k1_xor_e[x:x+6] for x in xrange(0, len(k1_xor_e), 6)]

    # We use each chunk as an address in an s-box.
    # Each group of six bits will give us an address in a different s-box.
    # Located at that address will be a 4 bit number.
    # This 4 bit number will replace the original 6 bits.
    # The net result is that the 8 groups of 6 bits are transformed into 8 groups of 4 bits making 32 bits in total.
    # For each s-box, the first and last bit of the 6 bits index the row of the box, the middle 4 index the column (we have 4 rows and 16 columns)
    s_box_output = ''
    for chunk_index in range(0, len(chunks)):
        chunk = chunks[chunk_index]

        # Get the first and last bit and convert it to a decimal, this will be the row index
        row_index = int(chunk[0] + chunk[5], 2)
        # Get the middle 4 bits and convert them to a decimal, this will be the column index
        column_index = int(chunk[1:5], 2)

        # Index the correct s-box, get the decimal value, convert to binary string
        decimal_value = s_boxes[chunk_index][row_index][column_index]
        s_box_output += ('{0:b}'.format(decimal_value)).zfill(4)

    # The final stage in the calculation of f is to do a permutation P of the s-box output to obtain the final value of f
    f_output = permutate_bits(s_box_output, f_p_box)

    # Now we have the output of the round function, we can finalise the following: R(n) = L(n-1) XOR f( R(n-1), K(n) )
    # We need to XOR L(n-1) and the output of the round function
    current_right_side = ('{0:b}'.format(int(previous_left_side, 2) ^ int(f_output, 2))).zfill(32)

    previous_right_side = current_right_side
    previous_left_side = current_left_side

# After 16 iterations, we will have the final halves in previous_right and previous_left arrays
# We reverse the order of the two blocks so that the right side comes BEFORE the left
reversed = previous_right_side + previous_left_side

# Now we apply a final permutation
ciphertext = permutate_bits(reversed, final_p_box)
print('Ciphertext: %s' % ciphertext)
