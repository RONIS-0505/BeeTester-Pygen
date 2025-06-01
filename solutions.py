from stepik_tester import fast_test


# example
@fast_test("https://stepik.org/media/attachments/lesson/1437509/tests_5978023.zip")
def move_min_elements(nums: list[int]) -> int:
    min_val = min(nums)
    f_pointer = 0

    ln_ = len(nums) - 1
    left, right = ln_, ln_

    while left > -1:
        if nums[left] != min_val:
            nums[right] = nums[left]
            right -= 1
            left -= 1

        elif nums[left] == min_val:
            f_pointer += 1
            left -= 1

    for i in range(f_pointer):
        nums[i] = min_val
