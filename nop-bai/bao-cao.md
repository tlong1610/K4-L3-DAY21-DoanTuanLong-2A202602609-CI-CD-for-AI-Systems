# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

<!--
HƯỚNG DẪN - đọc rồi XÓA TOÀN BỘ các khối chú thích này sau khi điền xong:

  - Giới hạn: KHÔNG QUÁ 1 TRANG A4, tương đương khoảng 450 - 550 từ nội dung.
  - Chỉ điền vào các chỗ ___ và các ô trong bảng. Không thêm mục mới.
  - Viết bằng câu hoàn chỉnh, không gạch đầu dòng cụt lủn.
  - Kiểm tra độ dài sau khi đã xóa hết chú thích:
        wc -w nop-bai/bao-cao.md
    và xem trước bản in bằng cách mở file trên GitHub rồi Ctrl+P / Cmd+P.
-->

| | |
|---|---|
| Họ và tên | Đoàn Tuấn Long |
| MSSV | 2A202602609 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/tlong1610/K4-L3-DAY21-DoanTuanLong-2A202602609-CI-CD-for-AI-Systems |
| Ngày nộp | 07/10/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | **0.8780** |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | **0.7149** | 0.8740 |
| 4 | 200 | 0.05 | 3 | 0.7014 | 0.8740 |
| 5 | 300 | 0.1 | 4 | 0.7123 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Lần chạy 3 có `f1_score` cao nhất (0.7149) trên tập holdout và vượt ngưỡng 0.65 với khoảng cách an toàn. Lần chạy có accuracy cao nhất là lần 1 (0.8780), không trùng với lần có F1 cao nhất. Điều này cho thấy accuracy bị lớp đa số chi phối: chênh 0.004 accuracy không nói lên mô hình bắt được lớp thu nhập cao tốt hơn. Accuracy của 4/5 lần chạy chỉ dao động trong khoảng 0.874 - 0.878, trong khi F1 dao động từ 0.605 đến 0.715. Lần chạy 2 (ít cây, `learning_rate` thấp, cây nông) bị underfit và là bộ duy nhất trượt ngưỡng. So sánh lần 4 với lần 3 cho thấy đánh đổi giữa `n_estimators` và `learning_rate`: giữ 200 cây nhưng giảm `learning_rate` xuống 0.05 làm F1 giảm còn 0.7014, nên khi giảm tốc độ học cần tăng số cây để bù lại.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập Adult mất cân bằng: chỉ 24,8% mẫu thuộc lớp thu nhập > 50K. Vì vậy một mô hình vô dụng, luôn trả lời "thu nhập thấp", vẫn đạt accuracy 0,752 nhưng có F1 bằng 0, vì không nhận ra được một người thu nhập cao nào. Nếu đặt ngưỡng trên accuracy, mô hình đó gần như qua được kiểm tra, và mô hình yếu như lần chạy 2 (accuracy 0,846) trông vẫn có vẻ chấp nhận được. F1 của lớp dương là trung bình điều hòa của precision và recall trên chính lớp thiểu số mà bài toán quan tâm, nên nó chỉ cao khi mô hình vừa tìm ra được nhiều người thu nhập cao, vừa ít gán nhầm. Lab không dùng `average="weighted"` hay `average="macro"`, vì hai cách này trộn thêm F1 của lớp đa số (thường trên 0,9). Kết quả bị kéo lên và ngưỡng 0,65 mất ý nghĩa: một mô hình bỏ sót phần lớn lớp dương vẫn có thể vượt qua.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Hướng dẫn viết cho GCP nhưng em chỉ có tài khoản AWS. | Code mẫu dùng `google-cloud-storage`, GCS và GCE. | Chuyển sang S3 + EC2 + `boto3` + `dvc[s3]`; CI dùng IAM user chỉ có quyền trên bucket, VM đọc model qua IAM role nên không cần copy file key. |
| `import mlflow` lỗi trên máy cá nhân (Python 3.12). | Venv mới thiếu `pkg_resources`, còn SQLAlchemy 2.1 đã bỏ class mà mlflow 2.13 cần. | Ghim `setuptools<81` và `sqlalchemy<2.1` trong `requirements.txt` để cả máy cá nhân lẫn CI cài giống nhau. |
| `git push` không kích hoạt pipeline; DagsHub báo không tìm thấy experiment. | Repo là fork nên Actions bị tắt mặc định; DagsHub không có experiment "Default". | Bật Actions cho fork; `train.py` tạo experiment theo biến `MLFLOW_EXPERIMENT_NAME`. |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

<!-- Lấy số liệu từ bảng ở mục 3.6 của tasks/buoc-3.md. -->

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | ___ | ___ |
| Bước 3 (thêm `train_batch2`) | ___ | ___ |

**Nhận xét:** ___

<!--
Một câu trả lời trung thực kiểu "f1 giảm 0,01 vì dữ liệu mới cùng phân phối, không mang
thêm thông tin mới" được đánh giá cao hơn kết luận sai rằng thêm dữ liệu luôn tốt hơn.
-->

---

## 5. Phần Bonus Đã Thực Hiện (nếu có)

- [x] Bonus 1 - Tracking MLflow từ xa với DagsHub: job Train ghi mọi run vào experiment `income-classifier-ci` trên DagsHub (ảnh `06-dagshub-mlflow.png`).
- [x] Bonus 2 - Điều chỉnh ngưỡng quyết định: ngưỡng 0,30 nâng F1 từ 0,7149 lên 0,7368 vì mô hình đang thiên về lớp đa số; ghi `best_threshold` vào `report.json` và MLflow.
- [x] Bonus 3 - Báo cáo precision / recall tự động: `src/evaluate.py` ghi `outputs/detail.txt` (lớp >50K: precision 0,81, recall 0,64; FN=45, FP=18). Nếu mục tiêu là tìm khách hàng thu nhập cao thì bỏ sót (FN) tốn kém hơn, nên nên ưu tiên recall bằng ngưỡng thấp hơn.
- [x] Bonus 4 - Hoàn trả về phiên bản trước: Train chỉ upload vào `artifacts/candidate/<sha>/`; Release so F1 với `artifacts/current/report.json`, chỉ đưa lên `current` và restart VM khi F1 mới ≥ F1 cũ, kết quả so sánh in trong log.
- [x] Bonus 5 - Cảnh báo lệch lạc dữ liệu: `train.py` tính `positive_rate` (0,248), in `::warning::` nếu lệch > 5 điểm % so với 24,8% và ghi vào `report.json`.
