import numpy as np


def normalize_image(image, normalize):
    mean = normalize['mean']
    std = normalize['std']
    image = std * image + mean
    return image


def hex_str2bool(hex_string):
    """
    Converts a hex string to boolean value (for pHash/wHash)
    :param hex_string: String of hex values
    :return: Boolean equivalent of the hex string
    """
    integerValue = 1
    for char in hex_string:
        integerValue *= 16
        if char == "0":
            integerValue += 0
        elif char == "1":
            integerValue += 1
        elif char == "2":
            integerValue += 2
        elif char == "3":
            integerValue += 3
        elif char == "4":
            integerValue += 4
        elif char == "5":
            integerValue += 5
        elif char == "6":
            integerValue += 6
        elif char == "7":
            integerValue += 7
        elif char == "8":
            integerValue += 8
        elif char == "9":
            integerValue += 9
        elif char == "a":
            integerValue += 10
        elif char == "b":
            integerValue += 11
        elif char == "c":
            integerValue += 12
        elif char == "d":
            integerValue += 13
        elif char == "e":
            integerValue += 14
        elif char == "f":
            integerValue += 15
    binary = bin(integerValue)
    output = []
    for i, element in enumerate(str(binary)):
        if i > 2:
            output.append(True if element == "1" else False)
    return np.asarray(output)


def convert_BSHW_to_SBCHW(x):
    """
    input : x torch tensor
    output: x torch tensor
    Converts a torch tensor given in dimensions:
    Batch_size * Sequence_Length * Height * Width (B S H W)
    to
    Sequence_Length * Batch_size * Input_Channels  * Height * Width (S B C H W)
    """
    assert len(x.shape) == 4

    x = x.unsqueeze(0)
    x = x.permute(2,1,0,3,4)
    return x


def convert_SBCHW_to_BSHW(x):
    """
    input : x torch tensor
    output: x torch tensor
    Converts a torch tensor given in dimensions:
    Sequence_Length * Batch_size * Input_Channels  * Height * Width (S B C H W)
    to
    Batch_size * Sequence_Length * Height * Width (B S H W)
    """
    assert len(x.shape) == 5

    x = x.squeeze(2) #only remove the second dimension to avoid squeezing batches of size 1
    x = x.permute(1,0,2,3)

    return x