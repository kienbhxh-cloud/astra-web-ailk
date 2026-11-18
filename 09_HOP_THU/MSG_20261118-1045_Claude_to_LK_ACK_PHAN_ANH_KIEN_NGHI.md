MSG_20261118-1045_Claude_to_LK_ACK_PHAN_ANH_KIEN_NGHI
ACK thư MSG_20261118-1034_LK_CLAUDE_PHAN_ANH_KIEN_NGHI. Claude ghi nhận 3 mục. Hạn mức dùng và cấp quyền connector do nền tảng quyết định, Claude không đổi được; Claude chỉ tối ưu phần mình kiểm soát.

ĐỀ XUẤT (Claude tự áp dụng từ phiên sau):
1. Token budget: chỉ đọc thư mới (lọc modifiedTime sau mốc đã xử lý) và đúng tệp liên quan Task ID; không đọc dàn trải; thư dài chỉ đọc phần cần.
2. Skill loading: nạp đúng skill khi cần; việc lặp lại giao cho script trên GitHub Actions (0 token), Claude chỉ xem log/kết quả.
3. Checkpoint: cuối mỗi phiên ghi 1 tệp trạng thái ngắn (đã làm / SHA / NEXT) vào 09_HOP_THU, để phiên mới bắt đầu từ đó, không phải đọc lại từ đầu.
4. Quy chuẩn: tên tệp ASTRA_DRIVER_<YYYYMMDD_HHMM>_<SENDER>_TO_<RECIPIENT>_<TASKID>_<TYPE>; 1 báo cáo/phiên; bỏ bước trung gian không cần.
5. Quyền connector lặp lại: cấp quyền trọn gói một lần (đã làm với GitHub App cho astra-web-ailk); khi hết hạn thì cấp lại tại cài đặt connector.
6. Đề nghị LK: gom việc theo lô trong một phiên thay vì nhiều phiên ngắn; nếu hay chạm trần, cân nhắc nâng gói.

LƯU Ý: chưa có thư mới của Gemini trong 09_HOP_THU sau thư spec 0820 (kiểm tra lúc 10:45).
