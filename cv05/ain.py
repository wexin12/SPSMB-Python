from matrix import plus, format, transform, multiply_constant, multiply, replace_row, determinant, vypocetobashu,convolution
from view import load, numpy_to_list, list_to_numpy, show

if __name__ == "__main__":
    kernel = [
        [0, -1, 0, -1, 0],
        [0, -1, 0, -1, 0],
        [1, -1, 0, 1, 0],
        [1, -2, 1, 1, 0],
        [0, -1, 0, 0, 0]
    ]
    kernel1 = [
        [0, -1, 0, 1, 0],
        [1, -1, 0, 1, 0],
        [0, -1, 5, 1, 0],
        [2, -1, 0, 1, -2],
        [0, -1, 0, 1, 0]
    ]
    kernel2 = [
        [0, 0, -1, 0, 0],
        [0, -1, -2, -1, 0],
        [-1, -2, 12, -2, -1],
        [0, -1, -2, -1, 0],
        [0, 0, -1, 0, 0]
    ]
    

    image = load("C:\\Users\\martin.klima\\Desktop\\SPSMB-Python\\cv05\\taliayang.png")
 
    img = numpy_to_list(image)
    new_img = convolution(img, kernel)
    new_img2 = convolution(img, kernel2)
    np_img = list_to_numpy(new_img2)
    show(np_img)

