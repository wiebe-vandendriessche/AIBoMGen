from datetime import datetime

# generate_cifar_test_files was used with following epochs:

epochs_list = [1, 3, 5, 10, 20, 50]
training_started = ["UTC: 2025-05-20 19:39:48,335", "UTC: 2025-05-20 19:39:47,891",
                    "UTC: 2025-05-20 19:39:35,070", "UTC: 2025-05-20 19:40:12,332", "UTC: 2025-05-20 19:40:12,605", "2025-05-20 20:08:39,963"]
aibom_started = ["UTC: 2025-05-20 19:40:08,780", "UTC: 2025-05-20 19:40:09,931",
                 "UTC: 2025-05-20 19:40:18,833", "UTC: 2025-05-20 19:40:43,500", "UTC: 2025-05-20 19:41:03,430", "2025-05-20 20:10:25,508"]
completion = ["UTC: 2025-05-20 19:40:09,110", "UTC: 2025-05-20 19:40:10,241",
              "UTC: 2025-05-20 19:40:19,013", "UTC: 2025-05-20 19:40:43,686", "UTC: 2025-05-20 19:41:03,616", "2025-05-20 20:10:25,717"]


def parse_utc(s):
    return datetime.strptime(s.replace("UTC: ", ""), "%Y-%m-%d %H:%M:%S,%f")


print(f"{'Epochs':>6} | {'Train (s)':>9} | {'AIBOM (s)':>9} | {'Total (s)':>9}")
print("-" * 42)
for i in range(len(epochs_list)):
    t_start = parse_utc(training_started[i])
    t_aibom = parse_utc(aibom_started[i])
    t_end = parse_utc(completion[i])
    train_time = (t_aibom - t_start).total_seconds()
    aibom_time = (t_end - t_aibom).total_seconds()
    total_time = (t_end - t_start).total_seconds()
    print(
        f"{epochs_list[i]:6} | {train_time:9.2f} | {aibom_time:9.2f} | {total_time:9.2f}")

# Optional: Basic insights
print("\nAnalysis:")
print("- Training time increases with epochs, as expected.")
print("- AIBOM generation overhead is relatively constant and small compared to training time.")
print("- Overhead does not appear to increase with training time or number of epochs.")
