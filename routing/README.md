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
| `--exclude LAYER` | 否 | 见下节。 |
| `--layers PATH` | 否 | 校验 `--exclude` 用的 `layers.json`，默认 `data/processed/layers/layers.json`。 |

退出码：0 成功；1 路线不可达（端点在栅格外、端点在阻挡格上、两点之间无路径）；2 输入无效（参数、配置、grid、slope 文件有问题，或写文件失败）。错误信息写到 stderr。成功时 stdout 打印一行：`routing/out/route_<name>.geojson <字节数>`。

`routing/config.json` 中每个参数都必须有 `value` 和含 `YYYY-MM-DD` 日期的 `basis`，否则以退出码 2 拒绝。当前代价函数为 `quadratic_slope`：`cost = cost_base + cost_coefficient * (slope / slope_limit_deg) ^ cost_exponent`。坡度超过 `slope_limit_deg` 或坡度缺失的格子代价为无穷（不可通行）。

## `--exclude`（F10 对照路线）

`--exclude LAYER` 从代价计算中去掉一个图层，输出 `routing/out/route_<name>_no_<LAYER>.geojson`。依据：`docs/research/nico-routing-spec.md` 第 5 节。

- 可用的 LAYER 只有 `data/processed/layers/layers.json` 中的图层 id（名称小写）：`slope`、`hillshade`、`ctx`。其他值以退出码 2 拒绝。可用 `--layers PATH` 指定另一份 `layers.json`。
- 只有 `routing/config.json` 的 `cost_inputs`（当前为 `["slope"]`）里的图层会改变路线。排除 `hillshade` 或 `ctx` 时路线与不排除相同，stderr 提示 "no effect on routing"。
- 排除 `slope` 时，每个格子代价为 `cost_base`，没有阻挡格（坡度上限和缺失值规则都来自坡度）。`slope_threshold_deg` 仍写配置值，但未应用，`cost_function` 里有说明。
- `name` 属性为 `<name>_no_<LAYER>`；`data_used` 为 `cost_inputs` 去掉被排除的图层；`max_slope_deg` 仍按 `slope.npy` 取值。

示例：

```powershell
.\.venv\Scripts\python.exe routing/route.py --name ea-01 --start-rc 500 500 --end-rc 900 1200 --exclude slope
```

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

## Coordinates and generated routes (English)

The coordinates in `route_<name>.geojson` are grid metres `[easting_m, northing_m]` in the DTM equirectangular projection on the sphere R = 3396190 m. They are **not** longitude/latitude. The web page must convert or reproject them before display.

Generated routes in `routing/out/` (`length_m` and `max_slope_deg` read from the GeoJSON properties):

| File | end_poi | length_m | max_slope_deg |
|---|---|---|---|
| `route_landing-poi-001.geojson` | poi-001 | 2697.21 | 19.82 |
| `route_landing-poi-002.geojson` | poi-002 | 3149.45 | 19.98 |
| `route_landing-poi-003.geojson` | poi-003 | 1460.42 | 17.81 |
| `route_landing-poi-004.geojson` | poi-004 | 2872.13 | 12.38 |

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

- [x] 毅力号（Perseverance）轨迹对照验证：已真实运行一次，结果见 `validation/out/report.json`。
- [x] `validation/params.json` 已锁定（`d1965fd`，2026-11-15 12:52:46 +0800）。

## 已知局限

- **穿角（corner-cutting）**：路线使用 8 邻接移动（对角步长 √2）。当两个阻挡格子在对角线上相邻时，对角移动可能从它们之间的角穿过，即使两个阻挡格子都是 `np.inf`。这是该方法已知的局限（规格书 `docs/research/nico-routing-spec.md` 4.7 第 4 条），v1 不做处理。
- **东西向坡度偏低**：`grid.json` 的 `known_issue` 记录，原生投影是标准纬线为 0 的等距圆柱投影。在纬度约 18.5° 处，东西向一个像素在地面上约 0.95 m，南北向为 1 m，因此坡度的东西向梯度分量约低估 5%。`route.py` 不做修正。
- **HiRISE 置信度图层 v1 不用**：代价只来自坡度，`data_used` 固定为 `["slope"]`。
- **最大坡度按像素中心取值**：`max_slope_deg` 只取路径经过的像素中心处的坡度值，不是线段上的连续最大值。
- **毅力号参考路径大部分顶点在 DTM 网格外**：约 74% 的顶点落在 DTM 网格之外。该数字来自 `validation/check_transform.py` 的输出，不在 `report.json` 里。
- **参考终点在最底行**：参考终点位于网格最底一行，离下边界 0.837908506160602 m（`report.json` 的 `reference_end_distance_to_lower_boundary_m`，不到 1 m）。参考路径在此处离开网格，不是自然停下。
- **PLACES 第 3 段与 MMGIS 不一致**：PLACES 第 3 段（sol 353-386）为 2147.661 m，MMGIS 为 2716.261 m。原因未解释，没有因此改动任何参数。

## 验证（对照毅力号轨迹）

### 复现

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe validation\check_transform.py
.\.venv\Scripts\python.exe validation\run_validation.py
```

`run_validation.py` 只能跑一次：`validation/out/report.json` 已存在时脚本自动中止。参数锁定在提交 `d1965fd`，运行日期 2026-11-15。

### 结果摘要

以下数字全部取自 `validation/out/report.json`，未重新计算。

| 项目 | 值 |
|---|---|
| 状态（`results.status`） | `ok` |
| 结论（`results.verdict`） | `weak match` |
| 路线长度 `route_length_m` | 726.9999252239116 m |
| 路线代价 `route_cost_find_path` | 738.766393561179 |
| 参考点数 | 899（下标 0 到 898） |
| 落在阻挡格上的参考点 | 0 / 899 |
| M0 平均距离 `mean_m` | 49.445414996329326 m |
| M0 最大距离 `max_m` | 129.4524803786412 m |
| M2 中位数 `median_m` | 34.27634306755558 m |
| M2 第 95 百分位 `p95_m` | 127.30067925012663 m |
| M3 `dtw_per_path_point_m` | 63.67146791146537 m |

M1（重合度）按容差给出，结论按 `d_tol` = 10 m 的 M1 判定（阈值：不低于 0.80 为 close match，0.50 到 0.80 为 partial match，低于 0.50 为 weak match）：

| `d_tol`（m） | M1 | `overlap_route` |
|---|---|---|
| 5 | 0.07940284502980417 | 0.13509480851389563 |
| 10（主要） | 0.14755217634069018 | 0.24674775741096597 |
| 25 | 0.29376957570963574 | 0.4213855464398009 |

端点误差：起点 0.3644000487209335 m，终点 0.3591385938369312 m。该误差含最多约 0.71 个像素（1 m/像素下约 0.71 m）的格心偏移，因为我们的路线止于格心。

### 如何理解

- 三个容差下的 M1 都低于 0.50，结论是 weak match。所有声明的容差和指标都已列出，包括不好的结果。
- 这个对照只是合理性检查，不是真值。毅力号的行驶轨迹不是步行者的最优路线。
- weak match 的原因未解释。可能的因素（未验证）：参考路径与 DTM 网格的重叠有限，参考终点贴近下边界，PLACES 与 MMGIS 在第 3 段不一致，以及代价函数只用坡度而漫游车选路还考虑别的因素。
