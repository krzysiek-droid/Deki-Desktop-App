def bubble_sort(arr):
    for iter_num in range(len(arr) - 1, 0, -1):
        for idx in range(iter_num):
            if arr[idx] > arr[idx + 1]:
                temp = arr[idx]
                arr[idx] = arr[idx + 1]
                arr[idx + 1] = temp
    sorted_array = arr
    return sorted_array


def merge_sort(unsorted_array):
    def merge(left_half, right_half):

        res = []
        while len(left_half) != 0 and len(right_half) != 0:
            if left_half[0] < right_half[0]:
                res.append(left_half[0])
                left_half.remove(left_half[0])
            else:
                res.append(right_half[0])
                right_half.remove(right_half[0])
        if len(left_half) == 0:
            res = res + right_half
        else:
            res = res + left_half
        return res

    if len(unsorted_array) <= 1:
        return unsorted_array
    middle = len(unsorted_array) // 2
    left_arr = unsorted_array[:middle]
    right_arr = unsorted_array[middle:]

    left_arr = merge_sort(left_arr)
    right_arr = merge_sort(right_arr)

    sorted_array = list(merge(left_arr, right_arr))
    return sorted_array


def insertion_sort(unsorted_array):
    for i in range(1, len(unsorted_array)):
        j = i - 1
        nxt_element = unsorted_array[i]

        while (unsorted_array[j] > nxt_element) and (j >= 0):
            unsorted_array[j + 1] = unsorted_array[j]
            j = j - 1
        unsorted_array[j + 1] = nxt_element
    sorted_array = unsorted_array
    return sorted_array


def selection_sort(unsorted_array):
    for idx in range(len(unsorted_array)):
        min_idx = idx
        for j in range(idx + 1, len(unsorted_array)):
            if unsorted_array[min_idx] > unsorted_array[j]:
                min_idx = j
        unsorted_array[idx], unsorted_array[min_idx] = unsorted_array[min_idx], unsorted_array[idx]

    sorted_array = unsorted_array
    return sorted_array
