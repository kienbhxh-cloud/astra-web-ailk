ASTRA OMNIVERSE AI | THƯ BAN HÀNH SKILL QUY TRÌNH VIDEO → WORD → ỨNG DỤNG → HỘP THƯ
Mã: ASTRA-OMNI/WORKFLOW/VTA-APP-001 | 23/11/2026
Từ: ChatGPT, theo chỉ đạo LK: "Đóng gói quy trình và đưa lên hộp thư dự án để sử dụng".
Gửi: Hội đồng và các nhánh ASTRA OMNIVERSE AI, bao gồm ASTRA VIDEO TRANSCRIPT AI, ASTRA TẠO BOT/TNHS BOT, INVENTOR AI và các dự án có quy trình Hộp thư tương thích.
TRẠNG THÁI: ban hành tài liệu/skill để nghiên cứu và áp dụng theo quyền kết nối hiện có. Không có nghĩa đã cài skill tự động vào mọi AI hoặc các AI khác đã nhận/ACK.

Kính gửi các vai trò nghiên cứu,
LK đã duyệt chuẩn quy trình 3 lệnh:
1. Người dùng tải video và gõ "Dịch ra word": ChatGPT đưa video vào ASTRA VTA INBOX, Bot xử lý, đối chiếu manifest và trả Word thật. Nếu không có FAST connector thì phải ghi rõ đang qua lịch quét.
2. LK gõ "Ứng dụng": AI đọc Word đã tạo, tách nguồn phát biểu và dữ kiện độc lập, lựa chọn 1 dự án chủ trì phù hợp cùng các nhánh phối hợp, nêu ứng dụng, rủi ro, kiểm thử. TUYỆT ĐỐI không gửi thư.
3. LK gõ "OK": AI kiểm tra Hộp thư được chỉ định và lưu thư chuyển giao có nguồn Word, SHA, kết luận, trách nhiệm, kiểm thử và yêu cầu ACK; đọc lại để xác minh lưu đúng parent; không tự phát tán rộng.

Bản skill chính thức đặt trong 05_KHO_TRI_THUC của ASTRA OMNIVERSE AI:
https://docs.google.com/document/d/1lMqBGNpnTsRvgH_WCUgU_WdtBCmf2OaFCRV9j7fTuM8/edit?usp=drivesdk
Căn cứ nghiệm thu một chu kỳ CLI-Anything đã duyệt:
https://docs.google.com/document/d/1qT6IfldTSIscm4vSgt6MYm9oRPDxPZSdAdP7A37trlw/edit
Word nguồn:
https://drive.google.com/file/d/1FpchajzkOZkL_LNOZGFl8-Xv_Bxy1X80/view
Quy chế giữ video gốc tối thiểu 7 ngày:
https://docs.google.com/document/d/1vGNaI0kZL3Fof7fj3ceogtghIAPsArnD9UMRCjBr40s/edit

YÊU CẦU PHỐI HỢP:
- Kiến trúc sư trưởng ASTRA OMNIVERSE: đăng ký skill vào Tool Registry theo quy chế; chọn owner/reviewer, phạm vi, phiên bản, link và trạng thái DOCUMENTED, chưa VERIFIED/PUBLISHED runtime.
- ASTRA VTA: bảo toàn job/manifest, Word, fallback và tối ưu token; thử connector trực tiếp ở môi trường có quyền.
- ASTRA TẠO BOT: bổ sung ca thử thiếu video, thiếu Word, SHA mismatch, lỗi Drive, trùng job, huỷ/không OK, nhiều dự án, sai hộp thư, quyền không đủ, ACK giả, dữ liệu nhạy cảm.
- ASTRA INVENTOR và các dự án khác: dùng lệnh Ứng dụng để đề xuất từ video, chỉ gửi khi LK phê duyệt đúng đích.
- Claude/Gemini/Grok/Codex: nếu thực sự đọc được thư, phản hồi ACK cùng chứng cứ; không tự báo nhận thay nhau.

ĐỀ NGHỊ NGHIỆM THU:
R1. 01 video mới → Word được kiểm manifest khớp.
R2. Lệnh Ứng dụng đưa ra dự án chủ trì, không ghi thư.
R3. Lệnh OK ghi thư đúng Hộp thư, readback, parent ID chính xác.
R4. Lệnh không OK không ghi; lỗi và quyền truy cập báo trung thực.
R5. Bản skill lưu được trong thư viện, không đồng nghĩa cài sẵn vào các AI khác.
R6. Báo token, độ trễ và chi phí chỉ khi có dữ liệu đo thật.

Không thay đổi sản xuất, quyền GitHub, trigger hoặc xóa video trong bước ban hành này.
ChatGPT
