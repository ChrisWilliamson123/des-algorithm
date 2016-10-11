# Function to rotate bits to the left
def rotate_left(binary_string, amount):
    length = len(binary_string)
    return binary_string[amount:length] + binary_string[0:amount]

# Function which will take a bit string and a p-box and permutate the bits accordingly
def permutate_bits(key, p_box):
    subkey = ''
    for index in p_box:
        subkey += key[index-1]
    return subkey

# Function to generate our subkey blocks based on a shift amounts list
def generate_blocks(left_side, right_side, shift_amounts):
    subkey_blocks = []
    subkey_blocks.append((left_side, right_side))

    for amount in shift_amounts:
        previous_block = subkey_blocks[len(subkey_blocks)-1]
        left_side_rotated = rotate_left(previous_block[0], amount)
        right_side_rotated = rotate_left(previous_block[1], amount)
        subkey_blocks.append((left_side_rotated, right_side_rotated))

    # Remove the initial block
    subkey_blocks.pop(0)

    concatedated_blocks = []
    for block in subkey_blocks:
        concatedated_blocks.append(block[0] + block[1])

    return concatedated_blocks

def generate_subkeys(key, p_box_56, shift_amounts, p_box_48):
    # The first step to getting a subkey is to use a 56 bit P-box to map bits of the original key to the subkey
    # Notice that indexes 8, 16, 24, 32, 40, 48, 56, and 64 are missing from the p_box_56 above
    permutated = permutate_bits(key, p_box_56)
    subkey_left = permutated[0:len(permutated)/2]
    subkey_right = permutated[len(permutated)/2:len(permutated)]

    # The next step of getting the subkeys is to generate 16 blocks of binary strings, based on the amount of bit rotations depending on which index we are at (shift_amounts)
    # The bit rotation is done on the previous block i.e C2 and D2 depend on C1 and D1
    concatenated_blocks = generate_blocks(subkey_left, subkey_right, shift_amounts)

    # We now do a permutation on each concatenated (left + right side) block, using a p-box with only 48 entries
    final_subkeys = []
    for i in concatenated_blocks:
        final_subkeys.append(permutate_bits(i, p_box_48))

    return final_subkeys
