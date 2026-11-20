# ASTRA AUTOMATED PATTERN DISCOVERY ENGINE — APDE 0.1

Ngày 20/11/2026. Bản thực thi hữu hạn theo MASTER-DISCOVERY-001, không phải hoàn tất mọi nhánh A–I.

1. **Kho bất biến:** RAW/ARCHIVE có bản gốc và mã băm. Dữ liệu được chọn bằng SHA-256; đổi một byte thì loader từ chối. Giữ cả v1 có lỗi và v2 sửa ngày 2006-09-21 ở các kho gốc.
2. **Registry nguồn:** nguồn ZIP, thành viên, hàm/lớp, chữ ký/tham số mặc định, nguyên mã, kết quả cũ và trạng thái nằm trong MODEL_REGISTER. Hàm tiện ích không là mô hình; không gộp hai bản AUDIT-007 chỉ vì trùng tên.
3. **Sinh giả thuyết:** grammar() tạo 15 AST từ 10 đặc trưng và phép sub/mul, kết hợp hai mức ridge thành 30 ứng viên. evaluate() chỉ nhận AST trong whitelist, tối đa sâu 3; không eval/exec. Đây là bộ sinh công thức giới hạn, chưa là hệ thống tự tạo mọi chương trình Python.
4. **Đặc trưng:** tần suất có prior 100 kỳ, hiện diện kỳ trước, đảo số, nghịch đảo khoảng cách theo kỳ, áp lực đầu/đuôi và cos modulo so với đuôi ĐB kỳ trước. Mọi đặc trưng của t đọc trước t. Hệ số và chuẩn hóa chỉ fit 2005–2014, dự báo các kỳ sau bằng hệ số cố định và lịch sử có sẵn lúc đó.
5. **Compiler/learner:** p=clip(p0+intercept+beta*z, epsilon,1-epsilon), beta=cov(z,Y-p0)/(1+ridge). Đây là hồi quy ridge một chiều cho Brier, không phải logistic hay mạng neural. Công thức mới không có quyền tự cài thư viện, thay metric, mở mạng hoặc đọc kết quả tương lai.
6. **Chọn/đánh giá:** chọn duy nhất trên 2015–2020, lưu SELECTED_BEFORE_EVALUATION trước tính loss 2021–2026. Lịch sử từng được xem nên không gọi tập sau là holdout mới. Mọi sửa grammar sau lần chạy phải có phiên bản/run khác, không ghi đè run đã có.
7. **Audit:** ledger nối băm lưu cả OK/ERROR; kết quả âm được giữ. Brier/log loss, calibration, top1/3/5 tách any-hit/nhãn khác nhau/số nháy; random baseline giải tích cùng ngày/cùng k; so theo năm. Paired circular block bootstrap 14 kỳ, 2.000 lần, seed cố định; Holm cho 9 so sánh đã nêu. p-value bootstrap xấp xỉ, không có cam kết xác nhận toàn bộ chương trình nghiên cứu cũ.
8. **Phản biện tự động:** test mọi AST bằng đổi/cắt tương lai; kiểm chuẩn hóa chỉ fit train, giữ nháy trùng, schema/hash, từ chối AST lạ. 12 stress run null/tín hiệu nhân tạo dùng cùng grammar. Lỗi CLI Gemini được sửa bằng bridge riêng, không chạm bản bảo tồn. Hệ thống chưa tự chữa mọi lỗi logic; thay đổi mã cần review và kiểm thử lại.
9. **Cổng prospective:** mặc định đóng. Muốn mở cần protocol hợp nhất và alpha toàn nghiên cứu, tái lập độc lập, ngưỡng/sensitivity phù hợp, mã/dự báo khóa trước quay với neo thời gian ngoài máy. Không xuất top10 cho hôm nay từ nghiên cứu này.

## Giả thuyết liên ngành mới H-DIGIT-PRESSURE-001

Với i=10a+b, đặt H_a(t-1) và T_b(t-1) là số nháy đầu a/đuôi b kỳ trước; f_w(i,t) là tần suất hiện diện w kỳ có làm trơn, chỉ đọc quá khứ. X_i,t = [(H_a-2.7)/2.7 - (T_b-2.7)/2.7] * [f_7(i,t)-f_90(i,t)]. Dự báo theo ridge nêu trên.

Giả thuyết: tương tác bất cân xứng đầu/đuôi và thay đổi tần suất có thông tin bổ sung. Không gọi đây là phát minh chưa từng có trên thế giới. Đã đưa vào APDE-029/030, không được chọn bởi tập selection. Không mở riêng tập evaluation để lựa chọn lại nó. Muốn kiểm chứng mạnh hơn: đăng ký beta/grammar mới trước tương lai và đối chiếu uniform/history bằng metric khóa; thực hiện đối chứng nhãn hoán vị theo ngày và tín hiệu cài trước khi nghiên cứu lần sau.

## Danh mục nghiên cứu A–I và bổ sung Master Skill

| Nhánh | Hướng đã lưu/đề xuất | Mốc kiểm chứng cần có | Trạng thái lần này |
|---|---|---|---|
| A rời rạc | vị trí, đối xứng đảo, modulo, hypergraph, đếm hàm phân biệt | đếm semantic trùng luật, đối chiếu vét cạn | phục hồi mã; đảo/modulo có trong grammar |
| B xác suất | Bayesian shrinkage, Markov, gap hazard, điểm đổi | baseline xác suất, null có cấu trúc, CI theo khối | shrinkage/gap và CI đã chạy; WP2 riêng chưa chạy |
| C kinh tế lượng | AR, nhân tố, HMM/chuyển trạng thái, tham số trôi | chuẩn hóa/fitting chỉ trên quá khứ; ổn định theo năm | giữ econometric.py; chưa tái chạy toàn bộ |
| D ML | logistic, boosting, sequence/Transformer, contrastive learning | nested time split, learning curve, tính thêm mọi trial | ridge nhỏ đã chạy; mô hình lớn chờ thiết kế/budget |
| E công thức | symbolic regression, genetic programming, AST search | grammar hữu hạn/complexity penalty, ledger kể cả thất bại | AST generator 30 ứng viên đã chạy |
| F thông tin | entropy, MI, nén, minimum description length | null giữ cấu trúc lấy mẫu; nén không chứng minh ngẫu nhiên | phục hồi nguồn, chưa chạy thêm MI/nén |
| G tối ưu | SAT/SMT/MaxSAT/MILP/CP-SAT/WMC | cận nghiệm và proof checker độc lập nếu tuyên bố UNSAT | gói PNP có benchmark nhỏ; chưa chứng nhận G2 tổng thể |
| H vật lý | thay thiết bị, vận hành, lồng/bóng, metadata trạm | hồ sơ vận hành/chứng cứ độc lập, tránh suy từ lịch số | chỉ giả thuyết; chưa có telemetry/thiết bị |
| I mới | digit-pressure interaction; invariance theo môi trường; dự báo có quyền abstain; stability selection/MDL | test chống miền/nhãn, đăng ký cơ chế abstain, sensitivity/power | digit-pressure đã vào grammar, còn lại đề xuất |

Đề nghị Master Skill thêm nguồn/quy tắc ID ổn định, AST hash và tính tương đương semantic, ba tầng evidence (mẫu lịch sử / quan hệ sau hiệu chỉnh / lợi thế prospective), budget theo lần đánh giá, cổng lỗi dữ liệu trùng toàn bộ kỳ, và lệnh CLI thực sự được kiểm tra. Không cài Skill v2 vào tài khoản hoặc sửa tệp của AI khác trong công việc này.
