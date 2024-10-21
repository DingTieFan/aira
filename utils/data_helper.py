import pandas as pd
import numpy as np
import os

# 函数
import calendar
def max_date_of_month(year, month):
    """
    返回指定年份和月份的最大日期
    """
    # 获取指定月份的最大日期
    max_day = calendar.monthrange(year, month)[1]
    
    # 构建最大日期的字符串表示
    max_date_str = f"{year}-{month:02d}-{max_day:02d}"
    
    return max_date_str

from datetime import datetime

def month_difference(date1, date2):
    """
    计算两个日期之间的月数差
    参数格式：'YYYY-MM'
    """
    year1, month1 = map(int, date1.split('-'))
    year2, month2 = map(int, date2.split('-'))
    
    # 将较大日期作为结束日期，较小日期作为起始日期
    if (year1, month1) > (year2, month2):
        year1, month1, year2, month2 = year2, month2, year1, month1
    
    # 计算月数差
    month_diff = (year2 - year1) * 12 + (month2 - month1)
    
    return month_diff

from datetime import datetime

def days_difference(date1_str, date2_str):
    """
    计算两个日期字符串之间的天数差
    参数格式：'YYYY-MM-DD'
    """
    if date2_str == '\\N':
        return 999999
    
    # 将日期字符串转换为日期对象
    date1 = datetime.strptime(date1_str, '%Y-%m-%d')
    date2 = datetime.strptime(date2_str, '%Y-%m-%d')
    
    # 计算日期差
    delta = date2 - date1
    
    # 返回天数差
    return delta.days


def days_difference_mnt(date1_str, date2_str):
    """
    计算两个日期字符串之间的天数差
    参数格式：'YYYY-MM-DD'
    """
    # 将日期字符串转换为日期对象
    date1 = datetime.strptime(date1_str, '%Y-%m')
    date2 = datetime.strptime(date2_str, '%Y-%m')
    
    # 计算日期差
    delta = date2 - date1
    
    # 返回天数差
    return delta.days


from datetime import datetime
from dateutil.relativedelta import relativedelta

def add_date_with_relativedelta(date_str, months):
    """
    给定一个日期字符串，使用 relativedelta 添加指定的月数和天数，返回新的日期字符串
    参数格式：'YYYY-MM-DD'
    """
    # 将字符串转换为日期对象
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 使用 relativedelta 计算新日期
    new_date_obj = date_obj + relativedelta(months=months)
    
    # 将新日期转换为字符串
    new_date_str = new_date_obj.strftime('%Y-%m-%d')
    
    return new_date_str

# 测试
date_str = '2023-01-15'
new_date_str = add_date_with_relativedelta(date_str, 0)
print("新日期：", new_date_str)


def date_agg(date1, date2):
    mob_list = []
    gc_list = []
    date_y = int(date1[:4])
    date_m = int(date1[5:7])
    date_tm = max_date_of_month(date_y, date_m)
    months = month_difference(date1, date2)
    for m in range(months+1):
        mob = m
        gc_date = add_date_with_relativedelta(date_tm, m)
        mob_list.append(mob)
        gc_list.append(gc_date)
    return mob_list,gc_list

# 当前逾期的概念(无还款状态)
## overdue_def_type 为逾期定义口径 1 表示 逾期口径为： 实还本金+实还利息 >= 应还本金+应还利息； 其他 逾期口径为： 实还本金 >= 应还本金 
## overdue_def_type 默认是 1
def cur_overdue_days(x, overdue_def_type):
    mob_date = x['gc_date']  #观察时间点

    due_date = x['应还时间']
    due_amt = x['应还本金']
    due_interest = x['应还利息']

    repay_date = x['实还时间']
    repay_amt = x['实还本金']
    repay_interest = x['实还利息']

    #本期如果是 实还本金+利息 大于等于 应还本金+利息 代表 本期 已还清 1 （无逾期：正常还款 、 提前还款、 提前还清）
    #本期如果是 实还本金+利息 小于 应还本金+利息 代表 本期 未还清 0（有逾期：未还或者部分还）
    if overdue_def_type == 1: # 逾期口径为： 实还本金+实还利息 >= 应还本金+应还利息 代表 无逾期
        repay_sts = 1 if repay_amt+repay_interest >= due_amt+due_interest else 0  
    else:
        repay_sts = 1 if repay_amt >= due_amt else 0   # 逾期口径为： 实还本金 >= 应还本金 代表 无逾期
    
    if due_date >= mob_date:  # 未到应还日，不予考虑，逾期天数为0
        return 0
    elif due_date < mob_date and repay_sts == 0:   # 已到应还日，但未还清，逾期天数为： 观察日-应还日
        return days_difference(due_date, mob_date)
    elif  due_date < mob_date and repay_sts == 1 and repay_date > mob_date: #到观察日已还，实还日在观察日之后，逾期天数为： 观察日-应还日
        return days_difference(due_date, mob_date)
    elif due_date < mob_date and repay_sts == 1 and repay_date <=  mob_date: #到观察日已还，实还日在观察日之后，当前口径 逾期天数为： 0
        return 0
    else:
        return 0
    
def MN(x):
    if x == 0:
        return 0
    elif x>=1 and x<=30:
        return 1
    elif x>=31 and x<=60:
        return 2
    elif x>=61 and x<=90:
        return 3
    elif x>=91 and x<=120:
        return 4
    elif x>=121 and x<=150:
        return 5
    elif x>=151 and x<=180:
        return 6
    # elif x>=181 and x<=210:
    #     return 7
    else:
        return 7


def transform_group(group, target_value):
    # 这个时候传进来的已经是 借据号+mob 的数据了，在此基础上再对 逾期状态 进行修正
    # 按mob正序排，第一次出现符合 核销状态 的 mob 记录下来。本 mob 和后面的mob的状态都设置为 核销状态。 但是余额不做任何动作
    # 保持 核销状态不变，余额变化 的效果
    import numpy as np
    group = group.sort_values(by='mob')
    first_occurrence_mob = group[group['M'] >= target_value]['mob'].min()
    if np.isnan(first_occurrence_mob):
        group['first_occurrence_mob'] = -1
        return group
        
    group.loc[group['mob'] >= first_occurrence_mob, 'M'] = target_value
    group['first_occurrence_mob'] = first_occurrence_mob
    return group

def dws_etl(loan_table_df, repayment_table_df, delinquency, chargeoff_cutoff):
    """
    dws etl function
    Args:
        data (pd.DataFrame): input dataframe
        delinquency (int): number of days since the last payment
        chargeoff_cutoff (int): number of days after which a chargeoff is considered
    Returns:
        pd.DataFrame: transformed dataframe
    """
        ### 参数设定
    #1、 逾期口径定义：1 表示 逾期口径为： 实还本金+实还利息 >= 应还本金+应还利息； 其他 逾期口径为： 实还本金 >= 应还本金 

    overdue_def_type = 2 if delinquency == "only principal" else 1
    #2、 核销状态 的参数。 自动核销天数节点：让用户选择是否自动核销以及自动核销的节点 -  99999(不自动核销)、90天(M4)、120天(M5)、150天(M6)、180天(M7)
    target_value_mapping = {
        "-": 99999,
        "180": 7,
        "150": 6,
        "120": 5,
        "90": 4,
        "60": 3
    }
    target_value = target_value_mapping.get(chargeoff_cutoff)

    lc_df2 = loan_table_df.copy()

    lp_df2 = repayment_table_df.copy()
    
    aa1 = lp_df2.merge(lc_df2[['借据号', '借款金额']], how='left', left_on='借据号', right_on='借据号')

    ###1、构建观察点 和 MOB
    lc_df2['mob'] = lc_df2['借款成功日期'].apply(lambda x: date_agg(str(x)[:7], '2017-01')[0])
    lc_df2['gc_date'] = lc_df2['借款成功日期'].apply(lambda x: date_agg(str(x)[:7], '2017-01')[1])
    df = lc_df2.explode(['mob','gc_date'])[['借据号', '借款金额', '借款期限', '借款利率', '借款成功日期','gc_date','mob']]

    ###2、拼接还款计划表和MOB数据
    df1 = df.merge(aa1,on='借据号',how='left')
    df1['tm_diff'] = 0

    # 条件1：应还时间 或者 实还时间 都在观察时间内的话 这些数据都应该留下， 对mob没有限制
    condition1 = (df1['gc_date'] >= df1['应还时间']) | (df1['gc_date'] >= df1['实还时间'])
    df1.loc[condition1, 'tm_diff'] = 1

    # 在条件1下， 需要处理mob=0的时候，其观察点时间都会小于应还时间， 如不提前还，会导致mob=0的数据都没有，此时需要留一条数据，期数为1的数据
    condition2 = (df1['mob'] == 0) & (df1['期数'] == 1)
    df1.loc[condition2, 'tm_diff'] = 1

    ###3、排除不需要的数据 并 修正 实还本金
    df1 = df1[df1['tm_diff']== 1]
    # 主要是 实还时间 晚于gc_data(MOB观察时间点),虽然还了，但是在观察点的当前时间没有还，所以 实还本金 应该为 0，其余的就直接取 实还本金
    df1['实还本金'] = df1.apply(lambda x : x['实还本金'] if x['实还时间'] <= x['gc_date'] else 0, axis=1)

    ###3、逾期期数bucket的计算
    ## overdue_def_type 参数是 逾期口径的定义。
    df2 = df1.copy()
    df2['overdue_days'] =  df2.apply(lambda x: cur_overdue_days(x, overdue_def_type),axis=1)
    tmpp1 = df2.groupby(['借据号', '借款金额_x', '借款成功日期', 'gc_date','mob']).agg({'overdue_days': 'max', '实还本金': 'sum'}).reset_index()
    # 计算余额
    tmpp1['余额'] = tmpp1['借款金额_x'] - tmpp1['实还本金']
    # 逾期天数映射到账龄
    tmpp1['M'] = tmpp1.apply(lambda x : MN(x['overdue_days']) ,axis=1)

    ###4、是否核销逻辑
    # 按观察时间来看，每个观察点上该月份的实际还款本金和利息
    # df1存储的是每个观察点之前的情况，特别是实还本金和利息做了修正，所有用这个数据进行按观察时间来看，实还本金和实还利息字段的加工
    df1['观察月份'] = df1['gc_date'].apply(lambda x: x[:7])
    df1['实还月份'] = df1['实还时间'].apply(lambda x: x[:7])
    gc_repay_info = df1[(df1['实还时间'] <= df1['gc_date']) & (df1['观察月份'] == df1['实还月份'])]
    #****存在一个月还好几笔的情况，需要出重月份，实还加和****
    gc_repay_info1 = gc_repay_info.groupby(['借据号', 'gc_date'], as_index=False).agg({'实还本金': 'sum', '实还利息': 'sum'})

    df3 = pd.DataFrame()
    if target_value == 99999:
        df3 = tmpp1
        df3['核销状态'] = 0
        df3['坏账核销金额'] = 0.0
        #gc_repay_info1 已经携带了 '实还利息' 字段
        df3 = df3.merge(gc_repay_info1, how='left', on=['借据号', 'gc_date'])
        df3['坏账回收金额'] = 0.0
        df3['累计实还利息'] = df3.groupby('借据号')['实还利息'].cumsum()

    else:  #参数设定：如果target_value == 99999 表示不自动核销，为4代表>90天核销、为5代表>120天核销、为6代表>150天核销、为7代表>180天核销
        df3 = tmpp1.groupby('借据号', as_index = False).apply(transform_group, target_value).reset_index()
        # 新增 核销状态, 坏账核销金额【第一次出现记录】, 坏账回收金额【实还本金】
        df3['核销状态'] = df3['M'].apply(lambda x: 1 if x == target_value else 0)
        df3['坏账核销金额'] = df3.apply(lambda x: x['余额'] if x['M'] == target_value and x['mob'] == x['first_occurrence_mob'] else 0.0 ,axis = 1)
        #gc_repay_info1 已经携带了 '实还利息' 字段 
        df3 = df3.merge(gc_repay_info1, how='left', on=['借据号', 'gc_date'])
        df3['坏账回收金额'] = df3[['M', '实还本金_y']].apply(lambda x: x['实还本金_y'] if x['M'] == target_value else 0.0 ,axis=1)
        df3['累计实还利息'] = df3.groupby('借据号')['实还利息'].cumsum()

    df3 = df3[['借据号', '借款金额_x', '借款成功日期', 'gc_date', 'mob', '余额', 'M', '核销状态', '坏账核销金额', '坏账回收金额', '实还利息', '累计实还利息']]
    # 本月状态
    df3['本月状态'] = df3[['余额', 'M']].apply(lambda x: 99 if x['余额'] == 0.0 else x['M'], axis=1).astype('int32')

    new_df=df3.set_index(['借据号','借款金额_x', '借款成功日期', 'gc_date', 'mob', '核销状态', '坏账核销金额',	'坏账回收金额', '实还利息', '累计实还利息', '本月状态', 'M'])['余额'].unstack(fill_value=0.0)
    new_df.columns.name=None
    new_df=new_df.reset_index()

    ### 组装成dws的表格样式
    ## 因加入核销的逻辑，M中的取值是在变化的。所以需要确定有多少M的取值
    M_series = df3.M.unique()

    dws_df = new_df.merge(lc_df2[['借据号', '借款利率', '借款期限']], how='left', left_on='借据号', right_on='借据号')

    dws_df['余额'] = new_df[M_series].sum(axis=1)

    ##做成上个月的字段
    dws_df2 = dws_df[['借据号', 'mob', '本月状态']+M_series.tolist()]
    dws_df2['mob_minus_1'] = dws_df2['mob'] + 1

    dws_df = dws_df.merge(dws_df2, how='left', left_on=['借据号', 'mob'], right_on=['借据号', 'mob_minus_1'])
    dws_df = dws_df.drop(columns=['mob_minus_1', 'mob_y'])

    name_dict = {'借据号' : '借据号'
    ,'借款成功日期' : '放款日期'
    ,'借款金额_x' : '放款金额'
    ,'余额' : '余额'
    ,'借款利率' : '利率'
    ,'借款期限' : '放款期限'
    ,'gc_date' : '统计日期'
    ,'mob_x' : 'mob'
    ,'0_x' : '正常余额'
    ,'1_x' : '余额M1'
    ,'2_x' : '余额M2'
    ,'3_x' : '余额M3'
    ,'4_x' : '余额M4'
    ,'5_x' : '余额M5'
    ,'6_x' : '余额M6'
    ,'7_x' : '余额M7'
    ,'8_x' : '余额M8'
    ,'本月状态_x': '本月状态'
    ,'0_y' : '上月正常余额'
    ,'1_y' : '上月余额M1'
    ,'2_y' : '上月余额M2'
    ,'3_y' : '上月余额M3'
    ,'4_y' : '上月余额M4'
    ,'5_y' : '上月余额M5'
    ,'6_y' : '上月余额M6'
    ,'7_y' : '上月余额M7'
    ,'8_y' : '上月余额M8'
    ,'本月状态_y': '上月状态'
    }

    dws_df = dws_df.rename(columns=name_dict)

    dws_columns = ['借据号', '放款日期', '放款金额', '利率', '放款期限', '统计日期', 'mob', '余额',
    '正常余额']+ ['余额M{}'.format(i) for i in range(1, max(M_series)+1)] +['上月正常余额'] + ['上月余额M{}'.format(i) for i in range(1, max(M_series)+1)] + [
        '核销状态', '坏账核销金额',	'坏账回收金额', '实还利息', '累计实还利息', '本月状态', '上月状态']
    dws_df = dws_df[dws_columns]
    
    #todo 现阶段数据标准中借据表中没有X维度字段，需要加上。
    dws_df = dws_df.merge(lc_df2[['借据号', '初始评级', '借款类型', '是否首标',
        '年龄', '性别', '手机认证', '户口认证', '视频认证', '学历认证', '征信认证', '淘宝认证', '历史成功借款次数',
        '历史成功借款金额', '总待还本金', '历史正常还款期数', '历史逾期还款期数']], how='left', left_on='借据号', right_on='借据号')

    return dws_df


def vintage(df, loan_term, loan_type, initial_rating):
    df_vintage_src = df[df.mob > 0]
    if loan_term:
        df_vintage_src = df_vintage_src[df_vintage_src['放款期限'] == int(loan_term)]
    if loan_type:
        df_vintage_src = df_vintage_src[df_vintage_src['借款类型'] == loan_type]
    if initial_rating:
        df_vintage_src = df_vintage_src[df_vintage_src['初始评级'] == initial_rating]
    
    df_vintage_src['放款月份'] = df_vintage_src['放款日期'].apply(lambda x: str(x)[:7])
    df_vintage_src['统计月份'] = df_vintage_src['统计日期'].apply(lambda x: str(x)[:7])
    df_vintage_src['M2+余额'] = df_vintage_src[['余额M{}'.format(i) for i in range(2, 8)]].sum(axis=1)
    d1 = pd.pivot_table(df_vintage_src,index='放款月份',columns='mob',values='M2+余额', aggfunc='sum')
    d2 = pd.pivot_table(df_vintage_src,index='放款月份',columns='mob',values='放款金额',aggfunc='sum')
    vintage_M2_gt = d1/d2
    f1 = vintage_M2_gt.index[-12: ]
    f2 = vintage_M2_gt.columns[ :12]
    vintage_df = vintage_M2_gt.loc[f1, f2] # type: ignore

    return vintage_df


def list_files(storage_path):
    files = [f for f in storage_path.iterdir() if f.is_file()]
    return files

def delete_file(file_path):
    """Delete a specified file from the storage directory."""
    if file_path.exists():
        os.remove(file_path)