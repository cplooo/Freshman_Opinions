# -*- coding: utf-8 -*-
"""
112學年度新生學習適應調查
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import re
import seaborn as sns
import streamlit as st 
import streamlit.components.v1 as stc 
#os.chdir(r'C:\Users\user\Dropbox\系務\校務研究IR\大一新生學習適應調查分析\112')

####### 資料前處理




####### 定義相關函數 (Part 1)
###### 載入資料
@st.cache_data(ttl=3600, show_spinner="正在加載資料...")  ## Add the caching decorator
def load_data(path):
    df = pd.read_pickle(path)
    return df

###### 計算次數分配並形成 包含'項目', '人數', '比例' 欄位的 dataframe 'result_df'
@st.cache_data(ttl=3600, show_spinner="正在處理資料...")  ## Add the caching decorator
def Frequency_Distribution(df, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1):
    ##### 将字符串按逗号分割并展平
    split_values = df.iloc[:,column_index].str.split(split_symbol).explode()  ## split_symbol=','
    #### split_values資料前處理
    ### 去掉每一個字串前後的space
    split_values = split_values.str.strip()
    ### 將以 '其他' 開頭的字串簡化為 '其他'
    split_values_np = np.where(split_values.str.startswith('其他'), '其他', split_values)
    split_values = pd.Series(split_values_np)  ## 轉換為 pandas.core.series.Series
    
    ##### 计算不同子字符串的出现次数
    value_counts = split_values.value_counts()
    #### 去掉 '沒有工讀' index的值:
    if dropped_string in value_counts.index:
        value_counts = value_counts.drop(dropped_string)
        
    ##### 計算總數方式的選擇:
    if sum_choice == 0:    ## 以 "人次" 計算總數
        total_sum = value_counts.sum()
    if sum_choice == 1:    ## 以 "填答人數" 計算總數
        total_sum = df.shape[0]
        
    ##### 计算不同子字符串的比例
    # proportions = value_counts/value_counts.sum()
    proportions = value_counts/total_sum
    
    ##### 轉化為 numpy array
    value_counts_numpy = value_counts.values
    proportions_numpy = proportions.values
    items_numpy = proportions.index.to_numpy()
    
    ##### 创建一个新的DataFrame来显示结果
    result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
    return result_df

###### 調整項目次序
##### 函数：调整 DataFrame 以包含所有項目(以下df['項目']與order的聯集, 實際應用時, df['項目']是order的子集)，且顺序正确(按照以下的order)
@st.cache_data(ttl=3600, show_spinner="正在加載資料...")  ## Add the caching decorator
def adjust_df(df, order):
    # 确保 DataFrame 包含所有滿意度值
    for item in order:
        if item not in df['項目'].values:
            # 创建一个新的 DataFrame，用于添加新的row
            new_row = pd.DataFrame({'項目': [item], '人數': [0], '比例': [0]})
            # 使用 concat() 合并原始 DataFrame 和新的 DataFrame
            df = pd.concat([df, new_row], ignore_index=True)

    # 根据期望的顺序重新排列 DataFrame
    df = df.set_index('項目').reindex(order).reset_index()
    return df











#######  读取Pickle文件
df_freshman_original = load_data('df_freshman_original.pkl')
###### 使用rename方法更改column名称: '學系' -> '科系'
df_freshman_original = df_freshman_original.rename(columns={'學系': '科系'})
###### 更改院的名稱: 理學->理學院, 資訊->資訊學院, 管理->管理學院, 人社->人文暨社會科學院, 國際->國際學院, 外語->外語學院
##### 定义替换规则
replace_rules = {
    '理學': '理學院',
    '資訊': '資訊學院',
    '管理': '管理學院',
    '人社': '人文暨社會科學院',
    '國際': '國際學院',
    '外語': '外語學院'
}
##### 应用替换规则
df_freshman_original['學院'] = df_freshman_original['學院'].replace(replace_rules)


####### 預先設定
###### 預設定院或系之選擇
global 院_系 
院_系 = '0'
###### 預設定 df_freshman 以防止在等待選擇院系輸入時, 發生後面程式df_freshman讀不到資料而產生錯誤
choice='財金系' ##'化科系'
df_freshman = df_freshman_original[df_freshman_original['科系']==choice]
# choice_faculty = df_freshman['學院'][0]  ## 選擇學系所屬學院: '理學院'
choice_faculty = df_freshman['學院'].values[0]  ## 選擇學系所屬學院: '理學院'
df_freshman_faculty = df_freshman_original[df_freshman_original['學院']==choice_faculty]  ## 挑出全校所屬學院之資料
# df_freshman_faculty['學院']  

###### 預設定 selected_options, collections
selected_options = ['化科系','企管系']
# collections = [df_freshman_original[df_freshman_original['學院']==i] for i in selected_options]
collections = [df_freshman_original[df_freshman_original['科系']==i] for i in selected_options]
# collections = [df_freshman, df_freshman_faculty, df_freshman_original]
# len(collections) ## 2
# type(collections[0])   ## pandas.core.frame.DataFrame
column_index = 7
dataframes = [Frequency_Distribution(df, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1) for df in collections]  ## 22: "您工讀次要的原因為何:"
# len(dataframes)  ## 2
# len(dataframes[1]) ## 6,5
# len(dataframes[0]) ## 5,5
# len(dataframes[2]) ##   23

##### 形成所有學系'項目'欄位的所有值
desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
# desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 

##### 缺的項目值加以擴充， 並統一一樣的項目次序
dataframes = [adjust_df(df, desired_order) for df in dataframes]
# len(dataframes)  ## 2
# len(dataframes[1]) ## 6
# len(dataframes[0]) ## 6, 從原本的5變成6 
# dataframes[0]['項目']
# '''
# 0              體驗生活
# 1         為未來工作累積經驗
# 2             負擔生活費
# 3              增加人脈
# 4    不須負擔生活費但想增加零用錢
# 5         學習應對與表達能力
# Name: 項目, dtype: object
# '''
# dataframes[1]['項目']
# '''
# 0              體驗生活
# 1         為未來工作累積經驗
# 2             負擔生活費
# 3              增加人脈
# 4    不須負擔生活費但想增加零用錢
# 5         學習應對與表達能力
# Name: 項目, dtype: object
# '''
global combined_df
combined_df = pd.concat(dataframes, keys=selected_options)
# combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])
# ''' 
#                    項目  人數      比例
# 化科系 0            體驗生活   0  0.0000
#     1       為未來工作累積經驗  13  0.3824
#     2           負擔生活費   2  0.0588
#     3            增加人脈   2  0.0588
#     4  不須負擔生活費但想增加零用錢   7  0.2059
#     5       學習應對與表達能力  10  0.2941
# 企管系 0            體驗生活   1  0.0417
#     1       為未來工作累積經驗   9  0.3750
#     2           負擔生活費   4  0.1667
#     3            增加人脈   2  0.0833
#     4  不須負擔生活費但想增加零用錢   2  0.0833
#     5       學習應對與表達能力   6  0.2500
# '''


####### 定義相關函數 (Part 2): 因為函數 'Draw' 的定義需要使用 'combined_df' 來計算 'unique_level0',  因此要放在以上 '預先設定' 之後才會有 'combined_df' 的值
###### 畫圖形(單一學系或學院, 比較圖形)
@st.cache_data(ttl=3600, show_spinner="正在處理資料...")  ## Add the caching decorator
def Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=pd.DataFrame(), selected_options=[]):
    ##### 使用Streamlit畫單一圖
    if 院_系 == '0':
        collections = [df_freshman, df_freshman_faculty, df_freshman_original]
        dataframes = [Frequency_Distribution(df, column_index, split_symbol, dropped_string, sum_choice) for df in collections]  ## 'dataframes' list 中的各dataframe已經是按照次數高至低的項目順序排列
        ## 形成所有學系'項目'欄位的所有值
        # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
        # desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
        #### 只看所選擇學系的項目(已經是按照次數高至低的項目順序排列), 並且反轉次序使得表與圖的項目次序一致
        desired_order  = [item for item in dataframes[0]['項目'].tolist()]  ## 只看所選擇學系的項目
        desired_order = desired_order[::-1]  ## 反轉次序使得表與圖的項目次序一致
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])
        # 获取level 0索引的唯一值并保持原始顺序
        unique_level0 = combined_df.index.get_level_values(0).unique()

        #### 設置 matplotlib 支持中文的字體: 
        # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
        # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        #### 设置条形的宽度
        bar_width = 0.2
        #### 设置y轴的位置
        r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
        #### 设置字体大小
        title_fontsize = 15
        xlabel_fontsize = 14
        ylabel_fontsize = 14
        xticklabel_fontsize = 14
        yticklabel_fontsize = 14
        annotation_fontsize = 8
        legend_fontsize = 14
        #### 绘制条形
        fig, ax = plt.subplots(figsize=(10, 6))
        # for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
        for i, college_name in enumerate(unique_level0):            
            df = combined_df.loc[college_name]
            # 计算当前分组的条形数量
            num_bars = len(df)
            # 生成当前分组的y轴位置
            index = np.arange(num_bars) + i * bar_width
            # index = r + i * bar_width
            rects = ax.barh(index, df['比例'], height=bar_width, label=college_name)
    
            # # 在每个条形上标示比例
            # for rect, ratio in zip(rects, df['比例']):
            #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.1%}', ha='center', va='bottom',fontsize=annotation_fontsize)
        ### 添加图例
        ax.legend(fontsize=legend_fontsize)

        # ### 添加x轴标签
        # ## 计算每个组的中心位置作为x轴刻度位置
        # # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
        # # group_centers = np.arange(len(dataframes[0]))
        # ## 添加x轴标签
        # # ax.set_xticks(group_centers)
        # # dataframes[0]['項目'].values
        # # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
        # ax.set_xticks(r + bar_width * (len(dataframes) / 2))
        # ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
        # # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
        
        ### 设置y轴刻度标签
        ax.set_yticks(r + bar_width*(len(dataframes) / 2))  # 调整位置以使标签居中对齐到每个条形
        ax.set_yticklabels(dataframes[0]['項目'].values, fontsize=yticklabel_fontsize)


        ### 设置标题和轴标签
        ax.set_title(item_name,fontsize=title_fontsize)
        # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
        ax.set_xlabel('比例',fontsize=xlabel_fontsize)
        ### 显示网格线
        plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
        plt.tight_layout()
        # plt.show()
        ### 在Streamlit中显示
        st.pyplot(plt)

    if 院_系 == '1':
        #### 設置中文顯示
        # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
        # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        #### 创建图形和坐标轴
        plt.figure(figsize=(11, 8))
        #### 绘制条形图
        ### 反轉 dataframe result_df 的所有行的值的次序,  使得表與圖的項目次序一致
        result_df = result_df.iloc[::-1].reset_index(drop=True)
        plt.barh(result_df['項目'], result_df['人數'], label=choice)
        #### 標示比例數據
        for i in range(len(result_df['項目'])):
            plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.1%}', fontsize=14)
        #### 添加一些图形元素
        plt.title(item_name, fontsize=15)
        plt.xlabel('人數', fontsize=14)
        #plt.ylabel('本校現在所提供的資源或支援事項')
        #### 调整x轴和y轴刻度标签的字体大小
        plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
        plt.legend(fontsize=14)
        #### 显示网格线
        plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
        #### 显示图形
        ### 一般顯示
        # plt.show()
        ### 在Streamlit中显示
        st.pyplot(plt)


    ##### 使用streamlit 畫比較圖
    # st.subheader("不同單位比較")
    if 院_系 == '0':
        collections = [df_freshman_original[df_freshman_original['科系']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index, split_symbol, dropped_string, sum_choice) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=selected_options)
    elif 院_系 == '1':
        collections = [df_freshman_original[df_freshman_original['學院']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index, split_symbol, dropped_string, sum_choice) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]        
        combined_df = pd.concat(dataframes, keys=selected_options)
        
    # 获取level 0索引的唯一值并保持原始顺序
    unique_level0 = combined_df.index.get_level_values(0).unique()

    #### 設置 matplotlib 支持中文的字體: 
    # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
    # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
    matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    #### 设置条形的宽度
    bar_width = 0.2
    #### 设置y轴的位置
    r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
    #### 设置字体大小
    title_fontsize = 15
    xlabel_fontsize = 14
    ylabel_fontsize = 14
    xticklabel_fontsize = 14
    yticklabel_fontsize = 14
    annotation_fontsize = 8
    legend_fontsize = 14
    #### 绘制条形
    fig, ax = plt.subplots(figsize=(10, 6))
    # for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
    for i, college_name in enumerate(unique_level0):            
        df = combined_df.loc[college_name]
        # 计算当前分组的条形数量
        num_bars = len(df)
        # 生成当前分组的y轴位置
        index = np.arange(num_bars) + i * bar_width
        # index = r + i * bar_width
        rects = ax.barh(index, df['比例'], height=bar_width, label=college_name)

        # # 在每个条形上标示比例
        # for rect, ratio in zip(rects, df['比例']):
        #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.1%}', ha='center', va='bottom',fontsize=annotation_fontsize)
    ### 添加图例
    ax.legend(fontsize=legend_fontsize)

    # ### 添加x轴标签
    # ## 计算每个组的中心位置作为x轴刻度位置
    # # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
    # # group_centers = np.arange(len(dataframes[0]))
    # ## 添加x轴标签
    # # ax.set_xticks(group_centers)
    # # dataframes[0]['項目'].values
    # # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
    # ax.set_xticks(r + bar_width * (len(dataframes) / 2))
    # ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
    # # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)

    ### 设置y轴刻度标签
    ax.set_yticks(r + bar_width*(len(dataframes) / 2))  # 调整位置以使标签居中对齐到每个条形
    ax.set_yticklabels(dataframes[0]['項目'].values, fontsize=yticklabel_fontsize)


    ### 设置标题和轴标签
    ax.set_title(item_name,fontsize=title_fontsize)
    # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
    ax.set_xlabel('比例',fontsize=xlabel_fontsize)
    ### 显示网格线
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.tight_layout()
    # plt.show()
    ### 在Streamlit中显示
    st.pyplot(plt)









####### 設定呈現標題 
html_temp = """
		<div style="background-color:#3872fb;padding:10px;border-radius:10px">
		<h1 style="color:white;text-align:center;"> 112學年度新生學習適應調查 </h1>
		</div>
		"""
stc.html(html_temp)
# st.subheader("以下調查與計算母體為大二填答同學1834人")
###### 使用 <h3> 或 <h4> 标签代替更大的标题标签
# st.markdown("##### 以下調查與計算母體為大二填答同學1834人")

###### 或者，使用 HTML 的 <style> 来更精细地控制字体大小和加粗
st.markdown("""
<style>
.bold-small-font {
    font-size:18px !important;
    font-weight:bold !important;
}
</style>
<p class="bold-small-font">以下調查與計算母體為大一填答同學 1674人</p>
""", unsafe_allow_html=True)

st.markdown("##")  ## 更大的间隔


# global 院_系
####### 選擇院系
###### 選擇 院 or 系:
院_系 = st.text_input('以學系查詢請輸入 0, 以學院查詢請輸入 1  (說明: (i).以學系查詢時同時呈現學院及全校資料. (ii)可以選擇比較單位): ')
if 院_系 == '0':
    choice = st.selectbox('選擇學系', df_freshman_original['科系'].unique())
    #choice = '化科系'
    df_freshman = df_freshman_original[df_freshman_original['科系']==choice]
    choice_faculty = df_freshman['學院'].values[0]  ## 選擇學系所屬學院
    df_freshman_faculty = df_freshman_original[df_freshman_original['學院']==choice_faculty]  ## 挑出全校所屬學院之資料

    # selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=['化科系','企管系'])
    # selected_options = ['化科系','企管系']
    # collections = [df_freshman_original[df_freshman_original['科系']==i] for i in selected_options]
    # dataframes = [Frequency_Distribution(df, 7) for df in collections]
    # combined_df = pd.concat(dataframes, keys=selected_options)
    # #### 去掉 level 1 index
    # combined_df_r = combined_df.reset_index(level=1, drop=True)
elif 院_系 == '1':
    choice = st.selectbox('選擇學院', df_freshman_original['學院'].unique(),index=0)
    #choice = '管理'
    df_freshman = df_freshman_original[df_freshman_original['學院']==choice]
    # selected_options = st.multiselect('選擇比較學的院：', df_freshman_original['學院'].unique(), default=['理學院','資訊學院'])
    # collections = [df_freshman_original[df_freshman_original['學院']==i] for i in selected_options]
    # dataframes = [Frequency_Distribution(df, 7) for df in collections]
    # combined_df = pd.concat(dataframes, keys=selected_options)


# choice = st.selectbox('選擇學系', df_freshman_original['科系'].unique())
# #choice = '化科系'
# df_freshman = df_freshman_original[df_freshman_original['科系']==choice]
# selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique())
# # selected_options = ['化科系','企管系']
# collections = [df_freshman_original[df_freshman_original['科系']==i] for i in selected_options]
# dataframes = [Frequency_Distribution(df, 7) for df in collections]
# combined_df = pd.concat(dataframes, keys=selected_options)
# # combined_df = pd.concat([dataframes[0], dataframes[1]], axis=0)



df_streamlit = []
column_title = []


####### 問卷的各項問題
####### Q7 大學「學費」主要來源（可複選）
with st.expander("7. 大學「學費」主要來源(多選):"):
    # df_freshman.iloc[:,7] ## 7大學「學費」主要來源（可複選）
    column_index = 7
    item_name = "大學「學費」主要來源(多選)"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    ##### 使用Streamlit畫單一圖 & 比較圖
    #### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    
st.markdown("##")  ## 更大的间隔  



###### Q8 學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源（可複選）
with st.expander("8. 學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源(多選):"):
    # df_freshman.iloc[:,8] ## 8學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源（可複選)
    column_index = 8
    item_name = "學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源(多選)"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    ##### 使用Streamlit畫單一圖 & 比較圖
    #### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    
st.markdown("##")  ## 更大的间隔  





