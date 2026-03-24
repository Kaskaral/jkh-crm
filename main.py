"""def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

    return arr

if __name__ == "__main__":
    unsorted_list = list(map(int, input("Введите неотсортированный список чисел через пробел: ").split()))
    sorted_list = bubble_sort(unsorted_list)

    with open('sorted_bubble.txt', 'w') as file:
        file.write(' '.join(map(str, sorted_list)))"""
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_index = i
        for j in range(i+1, n):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]

    return arr

if __name__ == "__main__":
    unsorted_list = [-2, 3, -5, 1, 4, 7, 0, -1]
    sorted_list = selection_sort(unsorted_list)

    with open('sorted_selection.txt', 'w') as file:
        file.write(' '.join(map(str, sorted_list)))
"""def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >=0 and key < arr[j] :
                arr[j+1] = arr[j]
                j -= 1
        arr[j+1] = key

    return arr

if __name__ == "__main__":
    unsorted_list = [5, 2, -3, 10, 0, -1]
    sorted_list = insertion_sort(unsorted_list)

    with open('sorted_insertion.txt', 'w') as file:
        file.write(' '.join(map(str, sorted_list)))
def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr)//2
        L = arr[:mid]
        R = arr[mid:]

        merge_sort(L)
        merge_sort(R)

        i = j = k = 0

        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1

if __name__ == "__main__":
    unsorted_list = [3, -2, 5, 1, -4, 7, -6]
    merge_sort(unsorted_list)

    with open('sorted_merge.txt', 'w') as file:
        file.write(' '.join(map(str, unsorted_list)))
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        less_than_pivot = [x for x in arr[1:] if x <= pivot]
        more_than_pivot = [x for x in arr[1:] if x > pivot]
        return quick_sort(less_than_pivot) + [pivot] + quick_sort(more_than_pivot)

if __name__ == "__main__":
    unsorted_list = [3, -2, 5, 1, -4, 7, -6]
    sorted_list = quick_sort(unsorted_list)

    with open('sorted_quick.txt', 'w') as file:
        file.write(' '.join(map(str, sorted_list)))"""