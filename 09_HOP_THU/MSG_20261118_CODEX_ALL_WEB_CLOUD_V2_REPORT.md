# WEB-CLOUD-V2 — báo cáo kiểm thử khép kín
Ngày 18/11/2026, 22:16 ICT. Người thực hiện: Kỹ sư Codex-Sam Altman, SIMULATED_ROLEPLAY / AI.
Kết luận: PARTIAL / chưa hoàn tất b-c. Không có khóa/token/secret trong báo cáo.

## Trạng thái từng mục
| Mục | FACT hoặc UNVERIFIED | Kết quả và bằng chứng |
|---|---|---|
| a — URL /docs/ | FACT: HTTP200; UNVERIFIED: render PC/iPhone | curl HTTPS từ cloud trả200,24705bytes. Playwright với systemChromium thử1280/390 nhưng ERR_CERT_AUTHORITY_INVALID của môi trường; không tắtTLS. iPhone vật lý chưa thử. |
| b — thư skill kích hoạt workflow | FACT: đúngworkflow chạy; FAIL: chưa cóREPLY | Input09_HOP_THU/MSG_20261118-2204_LK_ALL_TEST.md, marker[SKILL:TONG_HOP_BAO_CAO], dữ liệu tổng hợp LKủy quyền. Run1 Gemini404 modelcũ; run2 chẩnđoán404; run3 modelmới503UNAVAILABLE nhu cầucao. Không córeply giả. |
| c — REPLY GitHub→Drive qua webhook | UNVERIFIED / BLOCKED_BY_UPSTREAM | Không córeply thực vìGemini503, nên chưa có file để kiểm chiều này. Không coi uploadDrive thủcông làwebhookPASS. |
| d — MSG_test.md Drive→GitHub | FACT / PASS | UploadDrive lúc15:07:13UTC; GitHubcommit db1131294258e609c06fd47eaf138f5ce05bc321 lúc15:09:53UTC, messageBridge sync từ Drive: MSG_test.md. Nội dunghai phía khớp chínhxác; khoảng2phút40giây, dưới5phút. |
| e — webhooksecret sai | FACT / PASS | Actionsrun44332890929 success, JSONok:false,error:unauthorized; directHTTPPOST cũng200nhưngJSONtừchối. Hai canary tênREJECTED_CANARY khôngxuấthiện trongDrive khiđốichiếu. |

## Các run và commit
Source trước thử: b7f1cbf419cc15c5a92e121005ad30bf3ef25182.
Thư thử ban đầu: c2ab9a9bcdda6a7aaed464579a30596a9ad3d65d.
- Run1 https://github.com/kienbhxh-cloud/astra-web-ailk/actions/runs/44331816263
  FACT failure: GeminiHTTP404; Commit agent reply fatalpathspec vìkhôngcófile.
- Chẩn đoán antoàn: commit97cfdbb89b1399e5b3db609def089def87729f8e.
  ĐọcJSONerror, lọckey khỏi thôngbáo, exitcode1 khiAPIfailure đểkhôngvào commitreply.
- Run2 https://github.com/kienbhxh-cloud/astra-web-ailk/actions/runs/44332366057
  FACT failure404NOT_FOUND: providerbáo gemini-2.5-flash khôngcòncho newusers vàkhuyếnnghị gemini-3.8-flash.
- Cậpnhậtmodel theoAPImessage: b815bbb4d0392bfaf9ab5c5f7e3af57ed528f067.
- Thưretry: aea32c9ff8d25757a134cbc926dcd8445bb91efc.
- Run3 https://github.com/kienbhxh-cloud/astra-web-ailk/actions/runs/44332592221
  FACT failure: Gemini503UNAVAILABLE, model đang highdemand, dịchvụgợiý thửlại sau.
  Chưa có outputAI, không xácnhận b/c thànhcông.
- Teste workflow .github/workflows/astra-bridge-negative.yml:
  commit200db6c8664b83019186b73cf81abb8a9651f1f5.
  Triggercommit c45a0ecac53d83f9ecfc121464895bc894dbb7ec.
  Run https://github.com/kienbhxh-cloud/astra-web-ailk/actions/runs/44332890929
  success; URLtừGitHubSecret, secretSAI ngẫu nhiên, khônginURLhoặcsecret. Khôngdùngtokenđượcgửivàochat.
- Testd https://github.com/kienbhxh-cloud/astra-web-ailk/commit/db1131294258e609c06fd47eaf138f5ce05bc321
  Drive https://drive.google.com/file/d/1sEsjY_eCrlb4NBZzkb839cR-O7qynKJp/view

## Phạm vi xác minh cấu hình
FACT từ ảnhLK: GitHubđãlưu3tênsecret, setupBridge logOK, deploymentV1 tạođược, trigger syncDriveToGitHub tồn tại.
FACT thực chạy: secretURL dùngđược trongnegativeworkflow; PAT/trigger thựcđẩytestd sangGitHub.
UNVERIFIED: chu kỳchínhxác5phút khônghiện ởảnh cuối, nhưng đãquan sát mộtlần đồngbộdưới5phút.
FACT mãbridge tại source đãđọc bắtbuộcsecret, giới hạn tênMSG_/ASTRA_DRIVER_.
GiữPages main/root: phiênkhôngthayđổisettings. KhôngdùngmãCode.gs gốctrongthưGemini1532.

## Giới hạn và bước tiếp
1. KhiGeminihết503, retry mộtthư tổnghợp mới/cùngthư cócommitmới; theo dõi đúngASTRA Skill Agent Runner, khôngnhầmASTRA24/7SkillRunner.
2. Chỉghi bPASS khi runxanhVÀ cóREPLYthực; chỉghi cPASS khi mởfileDriveđúngtên vàso content vớiGitHub.
3. skill_agent hiện chỉlogHTTPwebhook; HTTP200khôngchứngminhok:true. Phảiđốichiếufile hoặc nângkiểmtraJSON ởlượt sửađượcreview.
4. LK mởURL /docs/ trênPCvàiPhonethật đểxácminhhiểnthị; khôngcoi390pxemulation làiPhone.
5. Khôngcóbí mật đượcghi vào mã/thư/issue/log/commit. Các chuỗibímật đãxuấthiệntrongchat không đượcnhắclạihay dùngtrongtest.
Khôngtựkhẳngđịnh cấu hìnhkhép kínhoàn tất. Trạng thái: d/ePASS; aHTTPPASSnhưngthiếtbịUNVERIFIED; bFAIL503; cUNVERIFIED.
