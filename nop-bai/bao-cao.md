# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

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

**Lý do:** Lần 3 có F1 cao nhất (0,7149). Lần có accuracy cao nhất (lần 1, 0,878) không phải lần có F1 cao nhất: accuracy chỉ dao động 0,874 - 0,878 trong khi F1 dao động 0,605 - 0,715, vì accuracy bị lớp đa số chi phối. Lần 2 (ít cây, cây nông, `learning_rate` thấp) bị underfit nên trượt ngưỡng. So với lần 3, lần 4 giảm `learning_rate` còn 0,05 mà giữ 200 cây thì F1 giảm, tức là giảm tốc độ học phải tăng số cây để bù lại.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Chỉ 24,8% mẫu thuộc lớp > 50K, nên mô hình luôn đoán "thu nhập thấp" vẫn đạt accuracy 0,752 nhưng F1 bằng 0, vì không tìm ra người thu nhập cao nào. F1 của lớp dương kết hợp precision và recall trên chính lớp thiểu số cần quan tâm, nên chỉ cao khi mô hình vừa tìm đủ vừa ít gán nhầm. Không dùng `average="weighted"`/`"macro"` vì chúng trộn F1 của lớp đa số (khoảng 0,92), kéo kết quả lên và làm ngưỡng 0,65 mất ý nghĩa. Em đã kiểm chứng: push bộ tham số yếu cho F1 = 0 dù accuracy = 0,752, Quality Gate chặn và Release bị bỏ qua (ảnh `07-quality-gate-chan.png`).

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Hướng dẫn dùng GCP, em chỉ có AWS. | Code mẫu dùng GCS/GCE. | Chuyển sang S3, EC2, `boto3`, `dvc[s3]`; VM đọc model qua IAM role. |
| `import mlflow` lỗi trên Python 3.12. | Thiếu `pkg_resources`; SQLAlchemy 2.1 không tương thích mlflow 2.13. | Ghim `setuptools<81`, `sqlalchemy<2.1`. |
| Push không kích hoạt pipeline. | Repo là fork nên Actions tắt mặc định. | Bật Actions cho fork trong tab Actions. |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.874 |
| Bước 3 (thêm `train_batch2`) | 0.7354 | 0.882 |

**Nhận xét:** Gấp đôi dữ liệu làm F1 tăng nhẹ 0,0205, nhưng holdout chỉ có 124 mẫu dương nên mức tăng này chỉ tương đương vài dự đoán đúng thêm. Hai nửa dữ liệu có cùng phân phối, nên dữ liệu mới không mang thêm nhiều thông tin. Điều được kiểm chứng là quy trình: commit dữ liệu tự kích hoạt cả 4 jobs và tự triển khai model mới (0,7354 ≥ 0,7149) lên VM.

---

## 5. Phần Bonus Đã Thực Hiện (nếu có)

- [x] Bonus 1 - Tracking MLflow từ xa với DagsHub: job Train ghi run vào experiment `income-classifier-ci` (ảnh `06`).
- [x] Bonus 2 - Điều chỉnh ngưỡng quyết định: ngưỡng 0,30 nâng F1 từ 0,7149 lên 0,7368; ghi vào `report.json` và MLflow.
- [x] Bonus 3 - Báo cáo precision / recall tự động: `outputs/detail.txt` (lớp > 50K: precision 0,81, recall 0,64). Bỏ sót người thu nhập cao (FN) tốn kém hơn nếu mục tiêu là tìm khách hàng, nên nên ưu tiên recall.
- [x] Bonus 4 - Hoàn trả về phiên bản trước: Release chỉ đưa candidate lên `artifacts/current/` khi F1 mới ≥ F1 cũ, kết quả in trong log.
- [x] Bonus 5 - Cảnh báo lệch lạc dữ liệu: cảnh báo nếu tỷ lệ lớp dương lệch > 5 điểm % so với 24,8%; ghi `positive_rate` vào `report.json`.
