import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 页面基础配置
# ==========================================
st.set_page_config(page_title="地星 × 欢乐海岸财务预测模型", layout="wide")

st.title("地星 × 欢乐海岸财务预测模型")
st.markdown("本工具用于控制核心变量，实时预测临展期与成熟期的收益，辅助股权与投资参考。")

# ==========================================
# 侧边栏：核心交互变量控制区
# ==========================================
st.sidebar.header("核心变量控制区")

st.sidebar.subheader("1. 基础流量与门票")
total_traffic = st.sidebar.slider(
    "园区年总人流（人）", 500000, 1500000, 1000000, step=50000,
    help="参考顺德欢乐海岸官方统计数据：年均入园总量约 100 万人次。"
)
ticket_price = st.sidebar.slider(
    "儿童门票单价（元）", 40, 100, 60, step=5,
    help="商业政策：实行『儿童购票、大人免费陪同』策略，降低家庭入店门槛。"
)

st.sidebar.subheader("2. 临展期变量（8-11月）")
ex_traffic_weight = st.sidebar.slider(
    "临展期客流占全年比例 (%)", 20, 60, 30,
    help="公式：临展期园区人流 = 园区年总人流 × 占比。由于包含暑假（8月）和国庆黄金周，预估权重较高。"
) / 100

ex_conv_rate = st.sidebar.slider(
    "临展门票转化率 (%)", 0.5, 5.0, 2.0, step=0.1,
    help="公式：临展门票买票人数 = 临展期园区人流 × 转化率。可测试实际吸客效应。"
) / 100

ex_other_revenue = st.sidebar.number_input(
    "临展期其余业态总收入（元）", value=120000,
    help="计算方式：4个月期间试水开展的室外研学、室内手工课、衍生文创售卖及瓶装饮品流水总和。"
)
ex_setup_cost = st.sidebar.number_input(
    "临展布置与前期投入（元）", value=200000,
    help="包含：场地简装、超微距作品制作、灯光布置、标本、活体费用。"
)
ex_staff_cost = st.sidebar.number_input(
    "临展期4个月总工资（元）", value=120000,
    help="包含：研学老师、助教、摄影师共3人的4个月基本薪酬及展位临时兼职导览费用。"
)

st.sidebar.subheader("3. 成熟期变量（正式开业年度）")
mat_conv_rate = st.sidebar.slider(
    "成熟期年门票转化率 (%)", 1.0, 6.0, 2.5, step=0.1,
    help="公式：年购票人数 = 园区年总人流 × 转化率。空间全面升级后的转化预测。"
) / 100

st.sidebar.markdown("**研学业务年服务人次预测：**")
hand_students = st.sidebar.number_input(
    "室内手工课（80元/人）年人次", value=3650,
    help="核心转化：日常到店散客。公式：年收入 = 人次（平均每节课10人） × 80 元。"
)
out_students = st.sidebar.number_input(
    "户外探索课（300元/人）年人次", value=3840,
    help="核心转化：联动顺峰山高客单研学。公式：年收入 = 人次（平均每节课10人） × 300 元。"
)
school_students = st.sidebar.number_input(
    "学校/ToB合作（200元/人）年人次", value=1440,
    help="核心转化：利用工作日周一至周五承接中小学/企业研学项目. 公式：年收入 = 人次 × 200 元。"
)

st.sidebar.markdown("**店内二消年收入预测：**")
cafe_revenue = st.sidebar.number_input(
    "餐饮（饮品/轻食）年收入（元）", value=400000,
    help="依托临街及天台休闲餐饮区，满足家长陪同等待及游客歇脚需求。"
)
cultural_revenue = st.sidebar.number_input(
    "文创（手工艺/超微距衍生品）年收入（元）", value=200000,
    help="融合郭老师的各类高品质手工艺品与地星独家的超微距艺术衍生品。"
)

st.sidebar.subheader("4. 成熟期变量：核心成本与投资")
invest_amount = st.sidebar.number_input("投资人总投入（万元）", value=300) * 10000
amortization_years = st.sidebar.slider(
    "装修折旧年限（年）", 3, 10, 8,
    help="固定资产摊销。公式：年折旧费 = 总投资额 ÷ 折旧年限。"
)
mat_staff_cost = st.sidebar.number_input(
    "成熟期团队年度总薪酬（元）", value=1000000,
    help="包含扩招后的正式员工（管理、研学导师、摄影后期、媒体运营、财务）及兼职的人力总开支。"
)
cafe_cultural_cost_rate = st.sidebar.slider(
    "餐饮文创商品成本率 (%)", 10, 50, 30,
    help="公式：(餐饮收入 + 文创收入) × 成本率。30% 意味着毛利率为 70%。"
) / 100
study_material_rate = st.sidebar.slider(
    "研学课程活动耗材及设备研发维护投入比例 (%)", 10, 30, 20,
    help="公式：研学整体收入 × 比例。用于手工材料、标本、户外工具包、设备研发、维护、预约系统开发等。"
) / 100
mat_operating_cost = st.sidebar.number_input(
    "年度空间运营能源及营销费（元）", value=300000,
    help="包含：场地全年的空调、水电费、网费、维护费以及推广宣传费。"
)

# ==========================================
# 核心逻辑计算区
# ==========================================
# 1. 临展期计算
ex_ticket_rev = total_traffic * ex_traffic_weight * ex_conv_rate * ticket_price
ex_total_rev = ex_ticket_rev + ex_other_revenue
ex_rent = ex_total_rev * 0.10
ex_total_cost = ex_rent + ex_setup_cost + ex_staff_cost + 20000 
ex_net_profit = ex_total_rev - ex_total_cost

# 2. 成熟期年度计算
mat_ticket_rev = total_traffic * mat_conv_rate * ticket_price
mat_study_hand_rev = hand_students * 80
mat_study_out_rev = out_students * 300
mat_study_school_rev = school_students * 200
mat_study_rev = mat_study_hand_rev + mat_study_out_rev + mat_study_school_rev

mat_total_rev = mat_ticket_rev + mat_study_rev + cafe_revenue + cultural_revenue

mat_rent = mat_total_rev * 0.10
mat_material_cost = (cafe_revenue + cultural_revenue) * cafe_cultural_cost_rate + mat_study_rev * study_material_rate
mat_depreciation = invest_amount / amortization_years

mat_total_cost_with_dep = mat_rent + mat_staff_cost + mat_material_cost + mat_operating_cost + mat_depreciation
mat_net_profit = mat_total_rev - mat_total_cost_with_dep
mat_cash_flow = mat_net_profit + mat_depreciation

# ==========================================
# 中央看板数据展示区
# ==========================================
tab1, tab2 = st.tabs(["阶段损益预测看板", "投资回报与保本底线精算"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("阶段一：临展期（今年8-11月）")
        st.markdown(f"**临展收益与成本账目明细：**")
        
        st.markdown("##### 临展期收入明细")
        st.markdown(f"├─ 展览门票收入: **¥{ex_ticket_rev:,.2f}**")
        st.markdown(f"└─ 其它业态收入: **¥{ex_other_revenue:,.2f}**")
        st.metric("临展营业总收入 (合计)", f"¥{ex_total_rev:,.2f}")
        
        st.markdown("##### 临展期成本明细")
        st.markdown(f"├─ 园区分成租金 (10%): **¥{ex_rent:,.2f}**")
        st.markdown(f"├─ 临展布置与前期投入: **¥{ex_setup_cost:,.2f}**")
        st.markdown(f"├─ 临展期4个月总工资: **¥{ex_staff_cost:,.2f}**")
        st.markdown(f"└─ 水电及基础杂费 (固定): **¥20,000.00**")
        st.metric("临展期总运营成本 (合计)", f"¥{ex_total_cost:,.2f}")
        
        st.write("---")
        if ex_net_profit > 0:
            st.success(f"临展期最终可截留纯利润：**¥{ex_net_profit:,.2f}**")
        else:
            st.error(f"临展期预计净亏损：**¥{ex_net_profit:,.2f}**")
            
    with col2:
        st.subheader("阶段二：成熟期（正规年度运营）")
        st.markdown(f"**成熟期年损益账目明细：**")
        
        st.markdown("##### 成熟期年收入明细")
        st.markdown(f"├─ 超微距展览门票收入: **¥{mat_ticket_rev:,.2f}**")
        st.markdown(f"├─ 研学课1：室内手工课: **¥{mat_study_hand_rev:,.2f}**")
        st.markdown(f"├─ 研学课2：户外探索课: **¥{mat_study_out_rev:,.2f}**")
        st.markdown(f"├─ 研学课3：学校ToB合作: **¥{mat_study_school_rev:,.2f}**")
        st.markdown(f"├─ 二消业态1：餐饮轻食收入: **¥{cafe_revenue:,.2f}**")
        st.markdown(f"└─ 二消业态2：手工衍生文创: **¥{cultural_revenue:,.2f}**")
        st.metric("成熟期年营业总收入 (合计)", f"¥{mat_total_rev:,.2f}", f"其中研学总贡献: ¥{mat_study_rev:,.2f}")
        
        st.markdown("##### 成熟期年成本明细")
        st.markdown(f"├─ 园区分成房租 (10%): **¥{mat_rent:,.2f}**")
        st.markdown(f"├─ 成熟期团队年度总薪酬: **¥{mat_staff_cost:,.2f}**")
        st.markdown(f"├─ 餐饮文创+研学物料耗材: **¥{mat_material_cost:,.2f}**")
        st.markdown(f"├─ 空间年度能源及营销推广: **¥{mat_operating_cost:,.2f}**")
        st.markdown(f"└─ 300万总投资资产年折旧: **¥{mat_depreciation:,.2f}**")
        st.metric("成熟期年运营总成本 (合计)", f"¥{mat_total_cost_with_dep:,.2f}")
        
        st.write("---")
        if mat_net_profit > 0:
            st.success(f"成熟期年度财务净利润（已扣折旧）：**¥{mat_net_profit:,.2f}**")
        else:
            st.error(f"成熟期年度预计净亏损：**¥{mat_net_profit:,.2f}**")

    # ==========================================
    # 🌟 重点修正：规范化色彩盘调用路径
    # ==========================================
    st.write("---")
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        st.subheader("成熟期年收入构成")
        df_rev_pie = pd.DataFrame({
            "业态板块": ['1. 展览门票收入', '2. 研学整体收入', '3. 咖啡餐饮二消', '4. 手工文创二消'],
            "年营业额": [mat_ticket_rev, mat_study_rev, cafe_revenue, cultural_revenue]
        })
        # 修正：px.colors.qualitative.Pastel
        fig_rev = px.pie(df_rev_pie, values='年营业额', names='业态板块', hole=0.3,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_rev.update_traces(textposition='inside', textinfo='percent+label')
        fig_rev.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_rev, use_container_width=True)
        
    with col_pie2:
        st.subheader("成熟期年成本构成")
        df_cost_pie = pd.DataFrame({
            "成本项目": ['1. 提成房租(10%)', '2. 团队总薪酬', '3. 业态物料与耗材', '4. 空间能源及营销', '5. 资产折旧摊销'],
            "年支出": [mat_rent, mat_staff_cost, mat_material_cost, mat_operating_cost, mat_depreciation]
        })
        # 修正：px.colors.qualitative.Safe
        fig_cost = px.pie(df_cost_pie, values='年支出', names='成本项目', hole=0.3,
                          color_discrete_sequence=px.colors.qualitative.Safe)
        fig_cost.update_traces(textposition='inside', textinfo='percent+label')
        fig_cost.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_cost, use_container_width=True)

with tab2:
    st.subheader("投资人回本周期预测")
    st.markdown("**核心财务逻辑：** 商业装修300万虽然属于现金支出，但在财务报表上是以“折旧”形式分年扣除。对于投资人而言，真正用于回收投资的是【年净利润 + 每年无需付现的折旧费 = 年真实净现金流】。")
    
    if mat_cash_flow > 0:
        payback_period = (invest_amount - ex_net_profit) / mat_cash_flow
        st.info(f"💡 在当前变量控制下，投资人预计可于 **{max(0.0, payback_period):.2f} 年** 内完全回本并进入净盈利期。")
    else:
        st.error("❌ 当前变量设定下成熟期现金流为负，无法回本，请调整左侧变量增加收入或控制固定成本！")
        payback_period = 0

    years = np.arange(0, 6)
    cash_flow_line = []
    current_balance = -invest_amount + (ex_net_profit if ex_net_profit > 0 else 0)
    cash_flow_line.append(current_balance)
    
    for y in years[1:]:
        current_balance += mat_cash_flow
        cash_flow_line.append(current_balance)
        
    trend_df = pd.DataFrame({
        '正式运营年限': [f"第 {y} 年" if y>0 else "初始投资" for y in years],
        '累计账面净现金 (元)': cash_flow_line
    })
    st.write("**投资人资金回笼与收益积累曲线：**")
    st.line_chart(data=trend_df, x='正式运营年限', y='累计账面净现金 (元)', color="#ff9900")

    st.write("---")
    st.subheader("空间年度安全保本底线测算")
    st.markdown("**盈亏平衡计算公式：** 保本营业额 = 固定成本 (薪酬+折旧+基础运营) ÷ (1 - 变动成本率 - 10%分成租金比例)")
    
    fixed_costs = mat_staff_cost + mat_operating_cost + mat_depreciation
    variable_rate = mat_material_cost / mat_total_rev if mat_total_rev > 0 else 0
    if (1 - variable_rate - 0.10) > 0:
        break_even_rev = fixed_costs / (1 - variable_rate - 0.10)
        st.warning(f"1300平综合空间每年必须做到 **¥{break_even_rev:,.2f}** 的营业额，才能刚好保证地星团队和投资人不亏损。")
    else:
        st.error("成本结构异常，变动成本占比过高。")
