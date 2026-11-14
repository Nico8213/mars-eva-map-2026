# routing

最小代价路线工具（角色 B）。在坡度栅格上用 `skimage.graph.route_through_array` 求最小代价路径，输出一个 GeoJSON Feature。

## 怎么运行

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe routing/route.py --name <name> (--start-rc ROW COL | --start-en EASTING NORTHING) (--end-rc ROW COL | --end-en EASTING NORTHING) [选项]
```

命令行参数：

| 参数 | 必需 | 说明 |
|---|---|---|
| `--name NAME` | 是 | 路线名，须匹配 `^[A-Za-z0-9_-]{1,64}$`。决定输出文件名。 |
| `--start-rc ROW COL` | 与 `--start-en` 二选一 | 起点，像素（行、列，整数）。 |
| `--start-en EASTING NORTHING` | 与 `--start-rc` 二选一 | 起点，投影坐标（米）。 |
| `--end-rc ROW COL` | 与 `--end-en` 二选一 | 终点，像素（行、列，整数）。 |
| `--end-en EASTING NORTHING` | 与 `--end-rc` 二选一 | 终点，投影坐标（米）。 |
| `--start-poi ID` | 否 | 起点 POI 的 id，写入 `start_poi`。不给则为 `null`。 |
| `--end-poi ID` | 否 | 终点 POI 的 id，写入 `end_poi`。不给则为 `null`。 |
| `--slope PATH` | 否 | 坡度数组，默认 `data/processed/slope.npy`。 |
| `--grid PATH` | 否 | 栅格元数据，默认 `data/processed/grid.json`。 |
| `--config PATH` | 否 | 代价参数，默认 `routing/config.json`。 |

退出码：0 成功；1 路线不可达（端点在栅格外、端点在阻挡格上、两点之间无路径）；2 输入无效（参数、配置、grid、slope 文件有问题，或写文件失败）。错误信息写到 stderr。成功时 stdout 打印一行：`routing/out/route_<name>.geojson <字节数>`。

`routing/config.json` 中每个参数都必须有 `value` 和含 `YYYY-MM-DD` 日期的 `basis`，否则以退出码 2 拒绝。当前代价函数为 `quadratic_slope`：`cost = cost_base + cost_coefficient * (slope / slope_limit_deg) ^ cost_exponent`。坡度超过 `slope_limit_deg` 或坡度缺失的格子代价为无穷（不可通行）。

## 输出文件

- 文件名：`route_<name>.geojson`
- 位置：`routing/out/`
- 内容：一个 GeoJSON `Feature`，几何为 `LineString`。坐标 `[easting_m, northing_m]` 取路径经过的像素中心，坐标系与 `grid.json` 相同。
- 写入方式：先写临时文件再替换；文件大小达到 52,428,800 字节时以退出码 2 拒绝。

`properties` 字段：

| 字段 | 内容 |
|---|---|
| `name` | 路线名，等于 `--name`。 |
| `start_poi` | `--start-poi` 的值，未给则为 `null`。 |
| `end_poi` | `--end-poi` 的值，未给则为 `null`。 |
| `length_m` | 按输出坐标计算的折线长度，米，保留 2 位小数。 |
| `max_slope_deg` | 路径经过的像素中心处的最大坡度，度，保留 2 位小数。 |
| `slope_threshold_deg` | 配置中的 `slope_limit_deg`。 |
| `data_used` | 固定为 `["slope"]`。 |
| `cost_function` | 代价函数和参数的文字描述（最长 500 字符）。 |
| `generated_from` | `commit=<git rev-parse HEAD 的结果，失败则为 unknown>; config=<配置全文 JSON>`。 |

输出不含任何验证指标。

## 网页（Charles）需要的路线文件

依据 `web/js/routes.js`，网页从 `web/public/data/routes/` 读取：

1. `index.json`：JSON 数组，列出路线文件名，例如 `["route_ea-01.geojson"]`。
2. `index.json` 中列出的每个 `route_<name>.geojson`：一个 `LineString` Feature。

网页弹窗读取的属性：`name`、`length_m`、`max_slope_deg`、`slope_threshold_deg`、`data_used`、`start_poi`、`end_poi`。

`route.py` 只写 `routing/out/`，不会复制文件，也不会更新 `index.json`。

当前状态（按目录内容核对）：

| 文件 | 状态 |
|---|---|
| `web/public/data/routes/index.json` | 存在，只列出 `route_ea-01.geojson`。 |
| `web/public/data/routes/route_ea-01.geojson` | 存在。是否由 `route.py` 生成，未核对。 |
| `routing/out/route_*.geojson` | 缺失。目录里只有 `.gitkeep`。 |
| 其他路线的网页副本和 `index.json` 条目 | 缺失。 |

缺失时网页的行为（依据 `routes.js`）：

- `index.json` 读取失败：状态区显示错误（`Could not load routes/index.json ...`），不创建路线图层，也不添加 "Routes" 开关。
- `index.json` 中列出的某个文件读取失败，或不是 `LineString` Feature：状态区显示该文件的错误，其余路线照常绘制。
- 文件中缺少某个属性：弹窗对应项显示 `n/a`。
- `index.json` 为空数组：不画路线，仍添加 "Routes" 开关。
- 文件在 `routing/out/` 但未复制到 `web/public/data/routes/` 或未列入 `index.json`：网页不显示。

## 已完成

- 读取真实的 `data/processed/grid.json` 和 `data/processed/slope.npy`。`grid.json` 优先读 `top_left_x_m`、`top_left_y_m`、`crs_wkt`，旧写法（`top_left.easting_m`、`top_left.northing_m`、`crs`）作为回退。缺失字段使用默认值并在 stderr 给出警告；字段类型错误以退出码 2 拒绝。
- nodata 处理：NaN、无穷、小于 0 或大于 90 度的值，以及 `grid.json` 中声明的 `nodata_value`，都视为缺失，代价为无穷。0 度是有效坡度。
- mmap：`slope.npy` 以只读内存映射打开，代价栅格按 1024 行一块计算，不整体转换。
- 三个必需测试，在 `routing/tests/test_blocked_cells.py`：
  - `test_full_wall_is_unreachable`
  - `test_single_gap_routes_through_gap`
  - `test_cost_finite_and_no_blocked_cells_on_route`

## 未完成

- 毅力号（Perseverance）轨迹对照验证：要等快照文件。
- F10 的 `--exclude` 开关：`route.py` 目前没有该参数。
- `validation/params.json` 尚未锁定：其中的 `[TBD-DATA]` 还没填完。

## 已知局限

- **穿角（corner-cutting）**：路线使用 8 邻接移动（对角步长 √2）。当两个阻挡格子在对角线上相邻时，对角移动可能从它们之间的角穿过，即使两个阻挡格子都是 `np.inf`。这是该方法已知的局限（规格书 `docs/research/nico-routing-spec.md` 4.7 第 4 条），v1 不做处理。
- **东西向坡度偏低**：`grid.json` 的 `known_issue` 记录，原生投影是标准纬线为 0 的等距圆柱投影。在纬度约 18.5° 处，东西向一个像素在地面上约 0.95 m，南北向为 1 m，因此坡度的东西向梯度分量约低估 5%。`route.py` 不做修正。
- **HiRISE 置信度图层 v1 不用**：代价只来自坡度，`data_used` 固定为 `["slope"]`。
- **最大坡度按像素中心取值**：`max_slope_deg` 只取路径经过的像素中心处的坡度值，不是线段上的连续最大值。
