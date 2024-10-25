# Firefly III Data Importer

将 MoneyWiz 导出的 CSV 数据，导入到 Firefly III 中。

思路以及步骤：
1. 首先，为了简单，保证 Firefly 是干净的，即每次操作前清空所有 Firefly 的数据；
2. 从 MoneyWiz 导出的数据中，分别创建账户和交易等信息；

导出时注意事项：
1. 选择格式为“CSV”；
2. 选择时间为“所有时间”；
3. 选择日期格式为“YYYY/MM/DD”；

导入时注意事项：
1. 先进行数据检查，如果有任何报错，先使用 MoneyWiz 修改对应数据，再重新导出数据并导入；
2. 所有账户（Account）都建立为“资产”账户，所以如果有“债务”账户，例如房贷等，需要导入数据之后在 Firefly III 中调整；
3. 如果有报错，请按照报错信息进行对应数据的修改；

使用方法：
1. 在 Firefly III 的“选项” -> “个人档案” -> “OAuth授权”中，创建“个人访问令牌”；
2. 将“个人访问令牌”内容，复制粘贴到 `firefly.py` 的 `Token` 处；
3. 运行 `python3 firefly-data-importer.py -f <csv文件路径> -p <FireflyIII服务端口，默认80>` 导入数据；