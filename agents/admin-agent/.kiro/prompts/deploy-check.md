# @deploy-check — 部署前檢查

執行部署前檢查清單：
1. 確認所有測試通過
2. 確認 docker-compose.prod.yml 配置正確
3. 確認環境變數完整（.env vs .env.example）
4. 確認 team.yaml instances 配置正確
5. 回報結果 + 是否可部署
