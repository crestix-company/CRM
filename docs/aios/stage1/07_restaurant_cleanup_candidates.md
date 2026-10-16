# Restaurant Cleanup Candidates — READ ONLY

- 判定は候補抽出であり、削除確定ではない。
- 会社名・担当者・電話・メール・token等は記録せず、UUIDの一方向pseudonym（MD5先頭12桁）だけを掲載。
- ルール: 飲食強シグナルがあり医療強シグナルがないactive record。混在・不明は除外してHUMAN_REVIEWへ送る。
- 観測: candidate companies 235、candidate active deals 375。
- この一覧は再実行時の照合用であり、apply入力にしてはならない。承認済みsecure exportをDB内で再生成すること。

## 依存集計

全候補合計: 担当者220、DealLineItem 303（うち金額情報あり145）、DealParticipant 997、SalesPerformanceEvent 19、MeetingBooking 19、Activity 20、Task 19、DeliveryProject 0、直接AuditLog 0。候補が属するOrganizationにはGoogle Calendar接続1件があるが、候補行との直接関係は確認できないため削除対象外。

## Company candidates (235)

| key | organizationId | name signal | industry signal | custom field signal | association edges | action |
|---|---|---|---|---|---:|---|
| 01c027ac7292 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 03b748969dbe | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 06511cc1f19a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 0688ecc5268e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 06980c567f48 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 0706b8b055b7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 08e72cda7c50 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 0951d3974fc0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 09a2f24fe4a1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 09dbd74c6a75 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 0b34fdb938bf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 0dea99e6bfba | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 10abba0d4f22 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 129eaaf190ef | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 12ac992b3168 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 12d2cba8e3ad | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 137ebb7db918 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 14e341d28d75 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 151f21b635ac | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 5 | HUMAN_REVIEW |
| 15f6f33b0f38 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 16557c1f75e8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 189821ca2380 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 18ceee50159c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 19f61bc3c3f6 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 3 | HUMAN_REVIEW |
| 1c3993964dc0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 216b9bcb287d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 231fa21e5bbd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 2386758121b4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 24c028c8fbde | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 2bad7629086c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 2be92da1336f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 2c83ab64a030 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 2d14d0e7b7e4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 2e86447b6693 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 2e929629252a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 30cc50ef222a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 3123820155e8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 32e48526ab2f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 33d1516a32af | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 36c04935ad8c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 371c81593a8b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 6 | HUMAN_REVIEW |
| 372ec54dc1c5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| 3907eb0ea443 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 39b83f7645fd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 39f627bb8c27 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 3a584da3d1c5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 3c4ee3c83893 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 3e405f8e6654 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 3e624afb1adf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| 3f1da801ad64 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 3f7e1a95a48d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 3ff1ddd72a22 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 419337e61b81 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 42d48558b82e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 43abba23bc70 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 43e7d6d8d014 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 441af6f4d859 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 45be36fd45b5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 5 | HUMAN_REVIEW |
| 460184669d1f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 48b2db2ffe39 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 6 | HUMAN_REVIEW |
| 497490c9d3c8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 49c6ea9ae80d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 4ab0cf001964 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | false | 3 | HUMAN_REVIEW |
| 4af0f90ec9e8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 4c35b793ed1d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 4ffa11c8fbc0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 507270ce494d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 51cd7ddadcf7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 533b495c7c28 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 53894bc9e13e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 54a1ef854249 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 570bd7cd7f6c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 57d127d0ce40 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 585fa270a85b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| 5a8f1341fdd3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 5bf43a5d09d3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 5cc174814fba | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 5d15f1e143cb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 5d54332ad097 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 3 | HUMAN_REVIEW |
| 5d8ec63c597e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 5eed94305ac8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 5f7f0ba0dc66 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 600936b24490 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 63f3fc0306ba | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 656c1e805c68 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| 6638efa47667 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 67052eb2a607 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 3 | HUMAN_REVIEW |
| 67ed65c028be | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 697106850d3c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 6d078c2eba34 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 6eec731f16aa | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 6f595e6e31bf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 706a438920fe | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 70c439b606d9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 719d452c6871 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 72d7d479e586 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 732fb5cc8a17 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 736ac010d7f2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 743c5a20f5d6 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 75186fa33e42 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 79ea7e8a4c94 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 7af0d175525c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 7b3a0ec2e104 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 7d2dd7b43f7b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 3 | HUMAN_REVIEW |
| 7d88aad2ca1c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 7ef46659075c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 80300e565f23 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | true | true | 3 | HUMAN_REVIEW |
| 84a10c50d302 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 87fa6c158010 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 89b4e956be34 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 8b61dda071fb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 8c609bc3e366 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 8cd9717d3346 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 2 | HUMAN_REVIEW |
| 8ce410b88bc8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 8d4403793a4c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 8eee8ef37665 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| 906936b8b459 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 90a22775fb57 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 9183078406cc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 927e2e081e51 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 932a58c3534e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 9485bd921422 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | false | 5 | HUMAN_REVIEW |
| 99c488e38c77 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 9b07cf06f9f6 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 9b4026b7ed28 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 9b508d9788a5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 2 | HUMAN_REVIEW |
| 9baecac6597a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 9bb6f20572c8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 3 | HUMAN_REVIEW |
| 9c547dd4e2af | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 9ca14cdc80fc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 9d07ced48747 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| 9e045c8d8135 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 9e2eef18ecfc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 9f106967c7ed | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 9f8d39876d51 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| 9fa9e18e3b0c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| 9fd7f6d1d36c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a0689d866d34 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| a1b2293327d1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a1cda37ed88d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a2d6f3bf2ca5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| a2ed85fee44b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a399eeec29b0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a4088e8fd843 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| a5cf61d0966c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a68a19001873 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a76ad7ba8479 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a85656e93cca | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| a86cda57305b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| a8c612b6a6f5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| a8fb969c830d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| aacd3ce8ead0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | false | 2 | HUMAN_REVIEW |
| aba6393c16e5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| ae67b53a0797 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| af0722e4e938 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| b165a733422b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| b167773e6973 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| b295723d00b0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| b33c17d81fa5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| b496289ff04f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| b64dda09fc8e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| b739d8f9aade | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| b7a5fd0c156b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| b7c221f8b3e4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| b90dc371e1b1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| ba1311365dc3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| baf630ab335c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| bbd84e8f8200 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| bbf8f980219b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| be05da58fdcc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| be7225c3b38c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| bf0181a9e3b4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| bf0420bbce49 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 5 | HUMAN_REVIEW |
| bf3ba05ef934 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| c0daea47982f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| c0df49c73ec0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| c30af994844c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| c45745ce53dc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| c50c403b1dd7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| c6345482cb05 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| c6dde958536b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| c78d38441054 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| c7b70acfc5e7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| c89c11091074 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| cc4c11bd2b33 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| ccedf21498c7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| cd0374487d70 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| cdb2eb791613 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| cdbcb7c27f8b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| cde9ac958b7f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| cef1998b2bed | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| d288c8d102b7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 4 | HUMAN_REVIEW |
| d52eea6e983e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| d7ab7886eed5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| d88c200b2cf7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| da5d4a034985 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| dba0202f2f78 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| dbe5e902876e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 2 | HUMAN_REVIEW |
| dc171ca25543 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| dc634759533c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| df0b673965cc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| dfb30933f58a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| e003cd553188 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| e125634bdbd8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| e16ee8e16e8b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| e1cddf434ba0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| e275a8b33931 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | true | true | 3 | HUMAN_REVIEW |
| e2c96a993798 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| e38910cf81e5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| e3b41acae4e7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| e54df2bd0cb4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| e664efc4d56b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| e8114bc35dab | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| e910c7d6f5ee | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | true | true | 3 | HUMAN_REVIEW |
| e92875407bbf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| e9cdae3fcb6b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| ea4dd5e28aa2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| eafdfc17afa5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| eb2f45294a96 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| ebe49e7ea034 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| ec1fe63524ae | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| edf66397838b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 0 | HUMAN_REVIEW |
| f079343e7228 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| f094d826f2da | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| f19fb4cfc993 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| f24263b20f45 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| f2c528821634 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| f3a36e4e3886 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | true | true | 3 | HUMAN_REVIEW |
| f6f425141fb6 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| f93bcfdb1ffa | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| f97a450307e5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| fad079f4a1f8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | false | false | true | 3 | HUMAN_REVIEW |
| fb57cda54dfa | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |
| ffaa60dab844 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 2 | HUMAN_REVIEW |
| ffc4046d077c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | true | false | true | 3 | HUMAN_REVIEW |

## Active Deal candidates (375)

| key | organizationId | business unit | status | line items | participants | events | bookings | action |
|---|---|---|---|---:|---:|---:|---:|---|
| 001d66b99ccd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 01727cafcdfb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 02206db72a86 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 02bb97b8cdcc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 031e4e9ab6b3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| 03ab1b635f85 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 2 | 0 | 0 | HUMAN_REVIEW |
| 0451533be0eb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 1 | 1 | 1 | HUMAN_REVIEW |
| 05b3f1f04282 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 05cfe39ef7b3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 06407f9963c4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 064970de5081 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 07916cbf89d8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 0793b2f8c77c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 07ee72f8a648 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 0a6e5fad37e2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 0b19a7baf183 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 0ba8fdcffdbf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 0c37b5a1c1c3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 0efea823af3b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 0f460d9043ab | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 0fb0086c3901 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 0fdd6d21f7db | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 10047d4a71fd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 104787c71ca4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 1 | 1 | 1 | HUMAN_REVIEW |
| 10515c570d2c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 1109e9a06e1d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 121f02d9ebf3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 1257b5ec778d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 1373b6ecff0b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 140d60ed7fd3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 14406b468f8e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 147fe12df915 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 14f89112763d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 159fa66ed889 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 180d49cf4e8a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 18e30d029918 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 19b9d7f8b498 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 1aad3d0f9ada | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 1b1d0d05f855 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 1b4b0ccd7585 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 1d442c25d1c5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 1ea677d96c81 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 1ee7a43700de | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 1f73a824c2e8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 202bf75fc0bb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 219f1a5d9194 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 21c4267a725e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 2252dbbbe695 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 22f71a4724fe | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 23ddcfe5d876 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 1 | 1 | 1 | 1 | HUMAN_REVIEW |
| 25066af9bda9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 264e8c2f0e80 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 266083369516 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 2 | 0 | 0 | HUMAN_REVIEW |
| 2827673fd32f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 285aa863f299 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 28824f10d4d0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 2892be90963b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 28c7a13c64c9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 28e950053d96 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 29868a80b71e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 1 | 1 | 1 | 1 | HUMAN_REVIEW |
| 29b4d03f5c70 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 2ab3ff6c8468 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 2c86ae565cec | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 3 | 1 | 1 | HUMAN_REVIEW |
| 2ecef3c13baa | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 2ef7158eef7a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 2f84533a0f73 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 301ca7c6b605 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 30be19760396 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3141504b8b8b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 320b04235c4b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 32a7c9dfb6a7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 330ef863a310 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 2 | 0 | 0 | HUMAN_REVIEW |
| 334048a9fe3c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 335f87a0ffab | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3485d88a776e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 34adcd3d5a43 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 34f184e93933 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 35b626e6c877 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3784938259e2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 380e992b7aa5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 39b0fdbec16f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 39d35b6d5acf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3ad9cda8d0d8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3b4244e1dc03 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3c06fd2db976 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 3dda45798d48 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3e036f8a6c93 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 3e6160e121fe | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 1 | 1 | 1 | HUMAN_REVIEW |
| 3fddfb49cc53 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 41f40380a430 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 42732eefda1a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 43133f01e2d9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 43ac621bc7ff | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 440656be6efd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 4615de2cc3f1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 467121c68d40 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 467adcad14d1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 46c5b4b2477f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 46d2244a5fa4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 478a9da3c648 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 49d6b89e802b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4a3a3509bc37 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4ab1636bbc6f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4aeac7d4cc71 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4af4a923b016 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4b48beb9102a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4c976fc59ab8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4d31adca0f78 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4d84b4e71cdc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 4d84c147b3b1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4e884898ea71 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4f0910254f88 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 4f279d264d22 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5038765d1f06 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 50561c5a40db | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 52f90d97544d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 53fd697124a9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 54a1d4bc20c0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5624c24c519a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 56b0e356eefd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 578d076cd444 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 57f62fbe38b4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 5849c4735593 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 595b61412d27 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 598dbb651ed0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 59b751e9b75b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 59ccda9d9991 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 59f68f1b189a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 5a52acb36d6d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 5a56d98d734e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5a9f79bdc224 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 5ade1aa3ecfa | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 5b0bf65d526b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5bef6f937f1a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5c6a0be3fece | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5e54eb7199da | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5ed508004b22 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5fd89dcac64d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 5fdf3e7d1d88 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 604831c353d0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 606ba643c5e2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 61686a0fdf9f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 6285abb2c1eb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 63634b170a5b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 639e16ac2c1d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 63eb9ad14813 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 6475e20647e4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 64b58d29e724 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 64ff9673acba | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 65284bb93c09 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 653de75a9494 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 65608ab6d075 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 662a0388cf93 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 669b5f957a23 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 669eeaad991f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 66c45c5abde9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 66fc8ec6827c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 678281310e98 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 695b7f65d11e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 6b6686162ad2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 4 | 3 | 0 | 0 | HUMAN_REVIEW |
| 6b84314e42cb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 6c0b7e885ceb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 6d1cdc6dce60 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 6d54c79ef681 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 72702f847e55 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 7286a4cacdda | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 7388499215d7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 2 | 0 | 0 | HUMAN_REVIEW |
| 738adb14c56e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 748bd6bd8fed | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 76982e177c5a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 777862ee250b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 1 | 2 | 1 | 1 | HUMAN_REVIEW |
| 7af6ec3dd92f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 7b64bdb4877a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 7c33ab00c9ef | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 7c75b6b0a342 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 7d02e06387b9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 7d7b47e35af2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 7de3bc20e483 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 2 | 0 | 0 | HUMAN_REVIEW |
| 7e2c4322cf66 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 7ee9f493184b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 80118834bcb6 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 809edb85abc3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 814641343d19 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 81a870567727 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| 81da615ed973 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8220d7d20841 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 82fe28d8faec | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 83d1219f90b0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 851d166d4b97 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 855e6e8e8883 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 864d7939feb9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 86dafd225b1d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8767b134251e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8887cdaaaf3b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 88c4218891c4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 891ce3b44bef | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 894011cc0a92 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 89bcdae583ae | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 89d354a8b9a2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 8a74422af08b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8b3055199239 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 2 | 0 | 0 | HUMAN_REVIEW |
| 8b4048d76d61 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8b5c59019295 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8b9e053cfeec | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8bea2a5043ea | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 8cb429b9fa85 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 8ce43284f097 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8d0f4c7e4c9f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8e1e58cb9986 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8f38454cbefe | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 8ff0792e27ed | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 916e20ec7d4f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 91eb27d199ca | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 92071e77f722 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 9208a7a080b1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 9240e3ac3c75 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 9249d3ea241f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 927f2a23502d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 92f05eae35fb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 9361646f1756 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 93cd45d87dcd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 93ff63758093 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 95a42ae95318 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 95ddfe88cf81 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 96b5796a482d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 976040e82887 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 97d89c201e60 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 983ed1fcc80b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 994fabd5cf76 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| 9b01084b1eaa | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 9b56cbb6dae5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| 9b7334419ccf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 9ca41de2c651 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| 9ded9b517523 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 9e2b43cedbab | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| 9e63a40976f4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| 9fe4202d28d0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a080f2e89744 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a0c269f115c0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| a13b023e1e5e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| a147ffbdca28 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| a149dce6fd52 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| a19c0ff5f210 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| a1c03999281a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a207c4fa3f2d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| a23c47315db4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| a375563cae72 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| a394c5679b13 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a43a13f3af9a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| a58e9f828bc7 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a60603950709 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a6e0e2e0d87c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a782a5da8767 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| a7aa95109a38 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| a90930f7d2f2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| a9cff64e1793 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| aa082eb45ac2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| aa0cc005d5ab | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| aa735024ed2c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| aab72e651f4b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| ab570fc3bb34 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| ab60998f09a4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| ababb3c28f14 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| ac635d593a9d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| ac6960b05bc0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| ace41e75dd21 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| ae5d6f552fe2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| af1fe5f4df0d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| af607aa2e0b4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 2 | 0 | 0 | HUMAN_REVIEW |
| aff31074e298 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| b18bbbf259b0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| b323acb2f8fc | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| b34d3c2914ac | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| b435cbd882ba | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| b4d73d319a3f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| b54db18c04d9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| b5a96890e506 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| b5b3ff5d20b9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| b69f943afcaf | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| b7797d4a2c04 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| bc1ba21bdb55 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| bd76104a4c72 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| bdc099b6d099 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| be184687fa9a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| be44d138bbe4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| bf28652a313c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| bff1359b349c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| c093cce35d36 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| c1d4f928666c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| c254c21fd4f2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| c4fa230d952f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 2 | 0 | 0 | HUMAN_REVIEW |
| c5657099e1bb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| c5f0ffe472fb | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| c6bd513bf114 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| c810489ce788 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| c8f7a823b077 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| ca4bc39a9f6d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| cacddc59b729 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| cbe2df44025a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| cc9816c89630 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| cd072a7bf6d9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| ce40f119f2ae | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| ce735cc5fd71 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| cf6de560eff4 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| cfce6e00c503 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| d614c778143e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| d707e3dfbd52 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| d79e775c0354 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| d83c1a481aea | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| d98348f0f81f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| db27b9b95654 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| db3269a18bf8 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| db61a63412ef | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| dbefa6ce376a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| dc2a44472e39 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| dc6ae4171bfd | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| dca65c4ddff1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| dcf3bf46d138 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| dd8a7f640311 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| dde3dcc7e9a2 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| de413620896f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| de8b5856ae47 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| dece9fea2538 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| df06bc43a543 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| df54b18fe126 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| df82e8ce2b1a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| df9a646eef2b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| e00f8d424f05 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| e03bb413e1f1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| e05dd0a8fb69 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| e12b91bfd85c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| e12d0263dced | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| e20d17f7156d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| e5a0167cfc76 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| e60943f9946a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| e6cbd842526b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| e71d91b9c3fe | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| e76dece3f529 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| e924bde2fe31 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 2 | 1 | 1 | HUMAN_REVIEW |
| e971e946eb29 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| ea73dfa1503a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| eb0f70e6839f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| eb41e3a546f9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| eb51ac7f2c51 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 2 | 1 | 1 | 1 | HUMAN_REVIEW |
| eeb0c03d6dbe | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| efa9886e82d1 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| f00353080b9f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| f0c43574eea9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| f0e743374351 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| f17efd30f1c5 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| f2e55af8d067 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| f2f5443f0ba9 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| f34a6f644bd0 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| f3a7a44ddb1b | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| f5304e0a2bed | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| f543881212ae | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| f550a3bd6605 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| f5551e531f6c | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| f6d6a2a524db | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| f7842bff739e | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| f80928f5a760 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| f8ee104ec841 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 3 | 3 | 0 | 0 | HUMAN_REVIEW |
| f93905fd9491 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| f9f2c09ec85d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | invalid | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| fa145feafa4d | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | open | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| fad9b6de3b3f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| fafc04807c85 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| fb7a4835a765 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| fbfdaf4fbd5f | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| fc1c53452335 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| fc39c1a99da3 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |
| fc960e666b03 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 1 | 3 | 0 | 0 | HUMAN_REVIEW |
| fe4cdc878f58 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | cancelled | 0 | 2 | 0 | 0 | HUMAN_REVIEW |
| ffa0b5cd941a | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | won | 2 | 3 | 0 | 0 | HUMAN_REVIEW |
| fffee36679ba | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | HD事業部 | lost | 0 | 3 | 0 | 0 | HUMAN_REVIEW |

## 判定

全件を現時点では **HUMAN_REVIEW**。80件のWON Deal、145件の金額付きline item、履歴/会議/担当者を含むため物理削除は不可。まず表示対象外またはsoft-delete案を、保持ポリシーと承認後にdry-runする。
