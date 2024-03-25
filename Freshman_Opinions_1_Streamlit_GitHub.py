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
# df_freshman_original = load_data(r'C:\Users\user\Dropbox\系務\校務研究IR\大一新生學習適應調查分析\112\GitHub上傳\df_freshman_original.pkl')

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
global 院_系, choice, df_freshman, choice_faculty, df_freshman_faculty, selected_options, collections, column_index, dataframes, desired_order, combined_df
###### 預設定院或系之選擇
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
# global combined_df
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


####### 定義相關函數 (Part 2): 因為函數 'Draw' 的定義需要使用 'dataframes','combined_df' 來進行相關計算, 因此要放在以上 '預先設定' 之後才會有 'dataframes', 'combined_df' 的值
###### 畫圖形(單一學系或學院, 比較圖形)
@st.cache_data(ttl=3600, show_spinner="正在處理資料...")  ## Add the caching decorator
def Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=pd.DataFrame(), selected_options=[], dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14, bar_width = 0.2, fontsize_adjust=0):
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
        # bar_width = 0.2
        #### 设置y轴的位置
        r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
        # #### 设置字体大小
        # title_fontsize = title_fontsize ##15
        # xlabel_fontsize = xlabel_fontsize  ##14
        # ylabel_fontsize = ylabel_fontsize  ##14
        # xticklabel_fontsize = 14
        # yticklabel_fontsize = 14
        # annotation_fontsize = 8
        # legend_fontsize = legend_fontsize  ##14
        #### 绘制条形
        fig, ax = plt.subplots(figsize=(width1, heigh1))
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
        if fontsize_adjust==0:
            ax.legend()
        if fontsize_adjust==1:
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
        
        ### 设置x,y轴刻度标签
        ax.set_yticks(r + bar_width*(len(dataframes) / 2))  # 调整位置以使标签居中对齐到每个条形
        if fontsize_adjust==0:
            ax.set_yticklabels(dataframes[0]['項目'].values)
            ax.tick_params(axis='x')
        if fontsize_adjust==1:
            ax.set_yticklabels(dataframes[0]['項目'].values, fontsize=yticklabel_fontsize)
            ## 设置x轴刻度的字体大小
            ax.tick_params(axis='x', labelsize=xticklabel_fontsize)
        # ax.set_yticklabels(dataframes[0]['項目'].values)
        # ax.set_yticklabels(dataframes[0]['項目'].values, fontsize=yticklabel_fontsize)


        ### 设置标题和轴标签
        if fontsize_adjust==0:
            ax.set_title(item_name)
        if fontsize_adjust==1:
            ax.set_title(item_name,fontsize=title_fontsize)
        
        # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
        if fontsize_adjust==0:
            ax.set_xlabel('比例')
        if fontsize_adjust==1:
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
        plt.figure(figsize=(width2, heigh2))
        #### 绘制条形图
        ### 反轉 dataframe result_df 的所有行的值的次序,  使得表與圖的項目次序一致
        result_df = result_df.iloc[::-1].reset_index(drop=True)
        # plt.barh(result_df['項目'], result_df['人數'], label=choice, width=bar_width)
        plt.barh(result_df['項目'], result_df['人數'], label=choice)
        #### 標示比例數據
        for i in range(len(result_df['項目'])):
            if fontsize_adjust==0:
                plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.1%}')
            if fontsize_adjust==1:
                plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.1%}', fontsize=annotation_fontsize)
            
        #### 添加一些图形元素
        if fontsize_adjust==0:
            plt.title(item_name)
            plt.xlabel('人數')
        if fontsize_adjust==1:
            plt.title(item_name, fontsize=title_fontsize)
            plt.xlabel('人數', fontsize=xlabel_fontsize)
        
        #plt.ylabel('本校現在所提供的資源或支援事項')
        #### 调整x轴和y轴刻度标签的字体大小
        if fontsize_adjust==0:
            # plt.tick_params(axis='both')
            ## 设置x轴刻度的字体大小
            plt.tick_params(axis='x')
            ## 设置y轴刻度的字体大小
            plt.tick_params(axis='y')
        if fontsize_adjust==1:
            # plt.tick_params(axis='both', labelsize=xticklabel_fontsize)  # 同时调整x轴和y轴 
            ## 设置x轴刻度的字体大小
            plt.tick_params(axis='x', labelsize=xticklabel_fontsize)
            ## 设置y轴刻度的字体大小
            plt.tick_params(axis='y', labelsize=yticklabel_fontsize)
        
        if fontsize_adjust==0:
            plt.legend()
        if fontsize_adjust==1:
            plt.legend(fontsize=legend_fontsize)
        
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
    # #### 设置条形的宽度
    # bar_width = 0.2
    #### 设置y轴的位置
    r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
    # #### 设置字体大小
    # title_fontsize = 15
    # xlabel_fontsize = 14
    # ylabel_fontsize = 14
    # xticklabel_fontsize = 14
    # yticklabel_fontsize = 14
    # annotation_fontsize = 8
    # legend_fontsize = 14
    #### 绘制条形
    fig, ax = plt.subplots(figsize=(width3, heigh3))
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
    if fontsize_adjust==0:
        ax.legend()
    if fontsize_adjust==1:
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

    ### 设置x,y轴刻度标签
    ax.set_yticks(r + bar_width*(len(dataframes) / 2))  # 调整位置以使标签居中对齐到每个条形
    if fontsize_adjust==0:
        ax.set_yticklabels(dataframes[0]['項目'].values)
        ax.tick_params(axis='x')
    if fontsize_adjust==1:
        ax.set_yticklabels(dataframes[0]['項目'].values, fontsize=yticklabel_fontsize)
        ## 设置x轴刻度的字体大小
        ax.tick_params(axis='x', labelsize=xticklabel_fontsize)
        
    


    ### 设置标题和轴标签
    if fontsize_adjust==0:
        ax.set_title(item_name)
        ax.set_xlabel('比例')
    if fontsize_adjust==1:
        ax.set_title(item_name,fontsize=title_fontsize)
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
###### Q1 性別
with st.expander("Q1. 性別:"):
    # df_freshman.iloc[:,1] ## 1性別
    column_index = 1
    item_name = "性別"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14, bar_width = 0.2, fontsize_adjust=0)    
    
st.markdown("##")  ## 更大的间隔 




###### Q2 身分別
with st.expander("Q2. 身分別:"):
    # df_freshman.iloc[:,2] ## 2身分別
    column_index = 2
    item_name = "身分別"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df, bar_width = 0.15)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q3 經濟不利背景（可複選）
with st.expander("Q3. 經濟不利背景（可複選）:"):
    # df_freshman.iloc[:,3] ## 3經濟不利背景（可複選）
    column_index = 3
    item_name = "經濟不利背景（可複選）"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df, bar_width = 0.15)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q4 文化不利背景（可複選）
with st.expander("Q4. 文化不利背景（可複選）:"):
    # df_freshman.iloc[:,4] ## 4文化不利背景（可複選）
    column_index = 4
    item_name = "文化不利背景（可複選）"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df, bar_width = 0.15)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=50,heigh1=20,width2=50,heigh2=20,width3=50,heigh3=20,title_fontsize=35,xlabel_fontsize = 34,ylabel_fontsize = 34,legend_fontsize = 34,xticklabel_fontsize = 30, yticklabel_fontsize = 35, annotation_fontsize = 34, bar_width = 0.2, fontsize_adjust=1)
    
st.markdown("##")  ## 更大的间隔 




###### Q5 原畢業學校之類型
with st.expander("Q5. 原畢業學校之類型:"):
    # df_freshman.iloc[:,5] ## 5原畢業學校之類型
    column_index = 5
    item_name = "原畢業學校之類型"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df, bar_width = 0.15)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q6 原畢業學校所在地區
with st.expander("Q6. 原畢業學校所在地區:"):
    # df_freshman.iloc[:,6] ## 6原畢業學校所在地區
    column_index = 6
    item_name = "原畢業學校所在地區"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df, bar_width = 0.15)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 






###### Q7 大學「學費」主要來源（可複選）
with st.expander("Q7. 大學「學費」主要來源(多選):"):
    # df_freshman.iloc[:,7] ## 7大學「學費」主要來源（可複選）
    column_index = 7
    item_name = "大學「學費」主要來源(多選)"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔  



###### Q8 學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源（可複選）
with st.expander("Q8. 學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源(多選):"):
    # df_freshman.iloc[:,8] ## 8學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源（可複選)
    column_index = 8
    item_name = "學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源(多選)"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)    

st.markdown("##")  ## 更大的间隔 




###### Q9 我的入學管道
with st.expander("Q9. 我的入學管道:"):
    # df_freshman.iloc[:,9] ## 9我的入學管道
    column_index = 9
    item_name = "我的入學管道"
    column_title.append(df_freshman.columns[column_index][1:])

    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df,width1=15,heigh1=9,width2=15,heigh2=9,width3=15,heigh3=9,title_fontsize=20,xlabel_fontsize = 19,ylabel_fontsize = 19,legend_fontsize = 19)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=15,heigh1=9,width2=15,heigh2=9,width3=15,heigh3=9,title_fontsize=20,xlabel_fontsize = 19,ylabel_fontsize = 19,legend_fontsize = 19,xticklabel_fontsize = 19, yticklabel_fontsize = 19, annotation_fontsize = 19,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔




###### Q10 得知本校最主要的管道
with st.expander("Q10. 得知本校最主要的管道(多選題):"):
    # df_freshman.iloc[:,10] ## 10得知本校最主要的管道（可複選）
    column_index = 10
    item_name = "得知本校最主要的管道(多選題)"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q11 決定就讀本校最主要的原因（可複選）
with st.expander("Q11. 決定就讀本校最主要的原因（可複選）:"):
    # df_freshman.iloc[:,11] ## 11決定就讀本校最主要的原因（可複選）
    column_index = 11
    item_name = "決定就讀本校最主要的原因（可複選）"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔




###### Q12 我選擇目前就讀「科系」的動機（可複選）
with st.expander("Q12. 我選擇目前就讀「科系」的動機（可複選）:"):
    # df_freshman.iloc[:,12] ## 12我選擇目前就讀「科系」的動機（可複選）
    column_index = 12
    item_name = "我選擇目前就讀「科系」的動機（可複選）"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q13 本校在我心目中的志願排序
with st.expander("Q13. 本校在我心目中的志願排序:"):
    # df_freshman.iloc[:,13] ## 13本校在我心目中的志願排序
    column_index = 13
    item_name = "本校在我心目中的志願排序"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q14 目前就讀科系在我心目中的志願排序
with st.expander("Q14. 目前就讀科系在我心目中的志願排序:"):
    # df_freshman.iloc[:,14] ## 14目前就讀科系在我心目中的志願排序
    column_index = 14
    item_name = "目前就讀科系在我心目中的志願排序"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔   




###### Q15 目前就讀科系與高中職/五專時期學科領域之關聯程度（範圍1～5；1為毫不相關；5為高度相關）
with st.expander("Q15. 目前就讀科系與高中職/五專時期學科領域之關聯程度（範圍1～5；1為毫不相關；5為高度相關）:"):
    # df_freshman.iloc[:,15] ## 15目前就讀科系與高中職/五專時期學科領域之關聯程度（範圍1～5；1為毫不相關；5為高度相關）
    column_index = 15
    item_name = "目前就讀科系與高中職/五專時期學科領域之關聯程度（範圍1～5；1為毫不相關；5為高度相關）"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q16 目前就讀科系之專業領域
with st.expander("Q16. 目前就讀科系之專業領域:"):
    # df_freshman.iloc[:,16] ## 16目前就讀科系之專業領域
    column_index = 16
    item_name = "目前就讀科系之專業領域 (「其他」選項包含不知所屬領域)"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q17 目前就讀學制
with st.expander("Q17. 目前就讀學制:"):
    # df_freshman.iloc[:,17] ## 17目前就讀學制
    column_index = 17
    item_name = "目前就讀學制"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q18 目前就讀科系是否舉辦下列新生活動（可複選）
with st.expander("Q18. 目前就讀科系是否舉辦下列新生活動（可複選）:"):
    # df_freshman.iloc[:,18] ## 18目前就讀科系是否舉辦下列新生活動（可複選）
    column_index = 18
    item_name = "目前就讀科系是否舉辦下列新生活動（可複選）"
    column_title.append(df_freshman.columns[column_index][1:])


    ##### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    ##### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
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

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 




###### Q19 對目前就讀科系的瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）
##### Q19-1 學習範圍與目標
with st.expander("Q19 對目前就讀科系的瞭解程度. Q19-1. 學習範圍與目標瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）:"):
    # df_freshman.iloc[:,20] ## 19-1學習範圍與目標
    column_index = 20
    item_name = "學習範圍與目標瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔 



##### Q19-2 學生畢業時需具備的核心能力
with st.expander("Q19-2. 學生畢業時需具備的核心能力瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）:"):
    # df_freshman.iloc[:,21] ## 19-2學生畢業時需具備的核心能力
    column_index = 21
    item_name = "學生畢業時需具備的核心能力瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q19-3 必、選修課程規劃及修課規定
with st.expander("Q19-3. 必、選修課程規劃及修課規定瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）:"):
    # df_freshman.iloc[:,22] ## 19-3必、選修課程規劃及修課規定
    column_index = 22
    item_name = "必、選修課程規劃及修課規定瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q19-4 課程與未來就業的關聯性
with st.expander("Q19-4. 課程與未來就業的關聯性瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）:"):
    # df_freshman.iloc[:,23] ## 19-4課程與未來就業的關聯性
    column_index = 23
    item_name = "課程與未來就業的關聯性瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q19-5 各課程所欲培養的能力
with st.expander("Q19-5. 各課程所欲培養的能力瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）:"):
    # df_freshman.iloc[:,24] ## 19-5各課程所欲培養的能力
    column_index = 24
    item_name = "各課程所欲培養的能力瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q19-6 畢業條件相關規定
with st.expander("Q19-6. 畢業條件相關規定瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）:"):
    # df_freshman.iloc[:,25] ## 19-6畢業條件相關規定
    column_index = 25
    item_name = "畢業條件相關規定瞭解程度（範圍1～5；1為非常不瞭解；5為非常瞭解）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



###### Q20 入學至今，我感覺目前就讀科系的總體課程狀況
##### Q20-1 課業挑戰性
with st.expander("Q20.入學至今，我感覺目前就讀科系的總體課程狀況. Q20-1.課業挑戰性（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,27] ## 20-1課業挑戰性
    column_index = 27
    item_name = "課業挑戰性（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q20-2 符合學習興趣
with st.expander("Q20-2. 符合學習興趣（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,28] ## 20-2符合學習興趣
    column_index = 28
    item_name = "符合學習興趣（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q20-3 教師專業度
with st.expander("Q20-3. 教師專業度（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,29] ## 20-3教師專業度
    column_index = 29
    item_name = "教師專業度（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q20-4 教師授課品質
with st.expander("Q20-4. 教師授課品質（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,30] ## 20-4教師授課品質
    column_index = 30
    item_name = "教師授課品質（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q20-5 整體滿意度
with st.expander("Q20-5. 整體滿意度（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,31] ## 20-5整體滿意度
    column_index = 31
    item_name = "整體滿意度（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



###### Q21 我對於本校所提供資源或支援事項的「期待程度」（範圍1～5；1為程度非常低；5為程度非常高）
##### Q21-1 期望彈性且有效率的學校行政
with st.expander("Q21 我對於本校所提供資源或支援事項的「期待程度」. Q21-1. 期望彈性且有效率的學校行政（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,33] ## 21-1期望彈性且有效率的學校行政
    column_index = 33
    item_name = "期望彈性且有效率的學校行政（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-2 期望便捷的選課查詢系統
with st.expander("Q21-2. 期望便捷的選課查詢系統（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,34] ## 21-2期望便捷的選課查詢系統
    column_index = 34
    item_name = "期望便捷的選課查詢系統（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-3 期望容易使用的學校網站
with st.expander("Q21-3. 期望容易使用的學校網站（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,35] ## 21-3期望容易使用的學校網站
    column_index = 35
    item_name = "期望容易使用的學校網站（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-4 期望豐富的專業圖書資源（含期刊、電子資料庫等）
with st.expander("Q21-4. 期望豐富的專業圖書資源（含期刊、電子資料庫等）（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,36] ## 21-4期望豐富的專業圖書資源（含期刊、電子資料庫等）
    column_index = 36
    item_name = "期望豐富的專業圖書資源（含期刊、電子資料庫等）（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-5 期望完善的圖書館設施
with st.expander("Q21-5. 期望完善的圖書館設施（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,37] ## 21-5期望完善的圖書館設施
    column_index = 37
    item_name = "期望完善的圖書館設施（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-6 期望與就業接軌的實習機制
with st.expander("Q21-6. 期望與就業接軌的實習機制（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,38] ## 21-6期望與就業接軌的實習機制
    column_index = 38
    item_name = "期望與就業接軌的實習機制（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-7 期望健全的生活、職涯及諮商輔導機制
with st.expander("Q21-7. 期望健全的生活、職涯及諮商輔導機制（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,39] ## 21-7期望健全的生活、職涯及諮商輔導機制
    column_index = 39
    item_name = "期望健全的生活、職涯及諮商輔導機制（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-8 期望完善的證照輔導與經費補助機制
with st.expander("Q21-8. 期望完善的證照輔導與經費補助機制（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,40] ## 21-8期望完善的證照輔導與經費補助機制
    column_index = 40
    item_name = "期望完善的證照輔導與經費補助機制（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-9 期望完善的競賽輔導與經費補助機制
with st.expander("Q21-9. 期望完善的競賽輔導與經費補助機制（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,41] ## 21-9期望完善的競賽輔導與經費補助機制
    column_index = 41
    item_name = "期望完善的競賽輔導與經費補助機制（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-10 期望豐富的國際交流資源（如交換生、雙聯學位等）
with st.expander("Q21-10. 期望豐富的國際交流資源（如交換生、雙聯學位等）（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,42] ## 21-10期望豐富的國際交流資源（如交換生、雙聯學位等）
    column_index = 42
    item_name = "期望豐富的國際交流資源（如交換生、雙聯學位等）（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-11 期望充足的多元學習機會
with st.expander("Q21-11. 期望充足的多元學習機會（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,43] ## 21-11期望充足的多元學習機會
    column_index = 43
    item_name = "期望充足的多元學習機會（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-12 期望國際化的學習環境
with st.expander("Q21-12. 期望國際化的學習環境（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,44] ## 21-12期望國際化的學習環境
    column_index = 44
    item_name = "期望國際化的學習環境（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-13 期望彈性且合理的修課安排
with st.expander("Q21-13. 期望彈性且合理的修課安排（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,45] ## 21-13期望彈性且合理的修課安排
    column_index = 45
    item_name = "期望彈性且合理的修課安排（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-14 期望完善的選課輔導與協助管道
with st.expander("Q21-14. 期望完善的選課輔導與協助管道（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,46] ## 21-14期望完善的選課輔導與協助管道
    column_index = 46
    item_name = "期望完善的選課輔導與協助管道（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-15 期望能增進廣博學習的通識課程
with st.expander("Q21-15. 期望能增進廣博學習的通識課程（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,47] ## 21-15 期望能增進廣博學習的通識課程
    column_index = 47
    item_name = "期望能增進廣博學習的通識課程（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-16 期望e化的教學與資訊環境
with st.expander("Q21-16. 期望e化的教學與資訊環境（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,48] ## 21-16期望e化的教學與資訊環境
    column_index = 48
    item_name = "期望e化的教學與資訊環境（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-17 期望實用的教學設備
with st.expander("Q21-17. 期望實用的教學設備（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,49] ## 21-17期望實用的教學設備
    column_index = 49
    item_name = "期望實用的教學設備（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-18 期望舒適的教室空間
with st.expander("Q21-18. 期望舒適的教室空間（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,50] ## 21-18期望舒適的教室空間
    column_index = 50
    item_name = "期望舒適的教室空間（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-19 期望豐富的社團活動資源
with st.expander("Q21-19. 期望豐富的社團活動資源（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,51] ## 21-19期望豐富的社團活動資源
    column_index = 51
    item_name = "期望豐富的社團活動資源（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-20 期望完善的住宿資源
with st.expander("Q21-20. 期望完善的住宿資源（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,52] ## 21-20期望完善的住宿資源
    column_index = 52
    item_name = "期望完善的住宿資源（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-21 期望良好的學生餐廳與膳食規劃
with st.expander("Q21-21. 期望良好的學生餐廳與膳食規劃（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,53] ## 21-21期望良好的學生餐廳與膳食規劃
    column_index = 53
    item_name = "期望良好的學生餐廳與膳食規劃（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-22 期望便利的校園生活機能
with st.expander("Q21-22. 期望便利的校園生活機能（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,54] ## 21-22期望便利的校園生活機能
    column_index = 54
    item_name = "期望便利的校園生活機能（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-23 期望乾淨整潔的校園環境
with st.expander("Q21-23. 期望乾淨整潔的校園環境（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,55] ## 21-23期望乾淨整潔的校園環境
    column_index = 55
    item_name = "期望乾淨整潔的校園環境（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-24 期望便利的交通機能
with st.expander("Q21-24. 期望便利的交通機能（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,56] ## 21-24期望便利的交通機能
    column_index = 56
    item_name = "期望便利的交通機能（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-25 期望清楚實用的租屋資訊
with st.expander("Q21-25. 期望清楚實用的租屋資訊（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,57] ## 21-25期望清楚實用的租屋資訊
    column_index = 57
    item_name = "期望清楚實用的租屋資訊（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q21-26 期望清楚實用的打工、獎助學金資訊
with st.expander("Q21-26. 期望清楚實用的打工、獎助學金資訊（範圍1～5；1為程度非常低；5為程度非常高）:"):
    # df_freshman.iloc[:,58] ## 21-26期望清楚實用的打工、獎助學金資訊
    column_index = 58
    item_name = "期望清楚實用的打工、獎助學金資訊（範圍1～5；1為程度非常低；5為程度非常高）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



###### Q22. 入學至今，我對於「本校現在」所提供資源或支援的滿意程度（範圍1～5；1為非常不滿意；5為非常滿意）
##### Q22-1 滿意於彈性且有效率的學校行政
with st.expander("Q22.入學至今，我對於「本校現在」所提供資源或支援的滿意程度. Q22-1.滿意於彈性且有效率的學校行政 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,60] ## 22-1滿意於彈性且有效率的學校行政
    column_index = 60
    item_name = "滿意於彈性且有效率的學校行政 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-2 滿意於便捷的選課查詢系統
with st.expander("Q22-2.滿意於便捷的選課查詢系統 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,61] ## 22-2滿意於便捷的選課查詢系統
    column_index = 61
    item_name = "滿意於便捷的選課查詢系統 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-3 滿意於容易使用的學校網站
with st.expander("Q22-3.滿意於容易使用的學校網站 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,62] ## 22-3滿意於容易使用的學校網站
    column_index = 62
    item_name = "滿意於容易使用的學校網站 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-4 滿意於豐富的專業圖書資源（含期刊、電子資料庫等）
with st.expander("Q22-4.滿意於豐富的專業圖書資源（含期刊、電子資料庫等） (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,63] ## 22-4  滿意於豐富的專業圖書資源（含期刊、電子資料庫等）
    column_index = 63
    item_name = "滿意於豐富的專業圖書資源（含期刊、電子資料庫等） (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][6:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-5 滿意於完善的圖書館設施
with st.expander("Q22-5.滿意於完善的圖書館設施 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,64] ## 22-5滿意於完善的圖書館設施
    column_index = 64
    item_name = "滿滿意於完善的圖書館設施 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][6:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-6 滿意於與就業接軌的實習機制
with st.expander("Q22-6.滿意於與就業接軌的實習機制 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,65] ## 22-6滿意於與就業接軌的實習機制
    column_index = 65
    item_name = "滿意於與就業接軌的實習機制 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][6:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-7 滿意於健全的生活、職涯及諮商輔導機制
with st.expander("Q22-7.滿意於健全的生活、職涯及諮商輔導機制 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,66] ## 22-7滿意於健全的生活、職涯及諮商輔導機制
    column_index = 66
    item_name = "滿意於健全的生活、職涯及諮商輔導機制 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][6:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-8 滿意於完善的證照輔導與經費補助機制
with st.expander("Q22-8.滿意於完善的證照輔導與經費補助機制 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,67] ## 22-8滿意於完善的證照輔導與經費補助機制
    column_index = 67
    item_name = "滿意於完善的證照輔導與經費補助機制 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][4:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-9 滿意於完善的競賽輔導與經費補助機制
with st.expander("Q22-9.滿意於完善的競賽輔導與經費補助機制 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,68] ## 22-9滿意於完善的競賽輔導與經費補助機制
    column_index = 68
    item_name = "滿意於完善的競賽輔導與經費補助機制 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][4:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-10 滿意於豐富的國際交流資源（如交換生、雙聯學位等）
with st.expander("Q22-10.滿意於豐富的國際交流資源（如交換生、雙聯學位等） (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,69] ## 22-10滿意於豐富的國際交流資源（如交換生、雙聯學位等）
    column_index = 69
    item_name = "滿意於豐富的國際交流資源（如交換生、雙聯學位等） (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-11 滿意於充足的多元學習機會（如輔系、雙主修等）
with st.expander("Q22-11.滿意於充足的多元學習機會（如輔系、雙主修等） (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,70] ## 22-11滿意於充足的多元學習機會（如輔系、雙主修等）
    column_index = 70
    item_name = "滿意於充足的多元學習機會（如輔系、雙主修等） (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-12 滿意於國際化的學習環境（如外語自學中心、外語情境教室、全英語教學等）
with st.expander("Q22-12.滿意於國際化的學習環境（如外語自學中心、外語情境教室、全英語教學等） (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,71] ## 22-12滿意於國際化的學習環境（如外語自學中心、外語情境教室、全英語教學等）
    column_index = 71
    item_name = "滿意於國際化的學習環境（如外語自學中心、外語情境教室、全英語教學等）(範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-13 滿意於彈性且合理的修課安排
with st.expander("Q22-13.滿意於彈性且合理的修課安排 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,72] ## 22-13滿意於彈性且合理的修課安排
    column_index = 72
    item_name = "滿意於彈性且合理的修課安排 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-14 滿意於完善的選課輔導與協助管道
with st.expander("Q22-14.滿意於完善的選課輔導與協助管道 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,73] ## 22-14滿意於完善的選課輔導與協助管道
    column_index = 73
    item_name = "滿意於完善的選課輔導與協助管道 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-15 滿意於能增進廣博學習的通識課程
with st.expander("Q22-15.滿意於能增進廣博學習的通識課程 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,74] ## 22-15滿意於能增進廣博學習的通識課程
    column_index = 74
    item_name = "滿意於能增進廣博學習的通識課程 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-16 滿意於e化的教學與資訊環境
with st.expander("Q22-16.滿意於e化的教學與資訊環境 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,75] ## 22-16滿意於e化的教學與資訊環境
    column_index = 75
    item_name = "滿意於e化的教學與資訊環境 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-17 滿意於實用的教學設備
with st.expander("Q22-17.滿意於實用的教學設備 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,76] ## 22-17滿意於實用的教學設備
    column_index = 76
    item_name = "滿意於實用的教學設備 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-18 滿意於舒適的教室空間
with st.expander("Q22-18.滿意於舒適的教室空間 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,77] ## 22-18滿意於舒適的教室空間
    column_index = 77
    item_name = "滿意於舒適的教室空間 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-19 滿意於豐富的社團活動資源
with st.expander("Q22-19.滿意於豐富的社團活動資源 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,78] ## 22-19滿意於豐富的社團活動資源
    column_index = 78
    item_name = "滿意於豐富的社團活動資源 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-20 滿意於完善的住宿資源
with st.expander("Q22-20.滿意於完善的住宿資源 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,79] ## 22-20滿意於完善的住宿資源
    column_index = 79
    item_name = "滿意於完善的住宿資源 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-21 滿意於良好的學生餐廳與膳食規劃
with st.expander("Q22-21.滿意於良好的學生餐廳與膳食規劃 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,80] ## 22-21滿意於良好的學生餐廳與膳食規劃
    column_index = 80
    item_name = "滿意於良好的學生餐廳與膳食規劃 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-22 滿意於便利的校園生活機能
with st.expander("Q22-22.滿意於便利的校園生活機能 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,81] ## 22-22滿意於便利的校園生活機能
    column_index = 81
    item_name = "滿意於便利的校園生活機能 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-23 滿意於乾淨整潔的校園環境
with st.expander("Q22-23.滿意於乾淨整潔的校園環境 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,82] ## 22-23滿意於乾淨整潔的校園環境
    column_index = 82
    item_name = "滿意於乾淨整潔的校園環境 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-24 滿意於便利的交通機能
with st.expander("Q22-24.滿意於便利的交通機能 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,83] ## 22-24滿意於便利的交通機能
    column_index = 83
    item_name = "滿意於便利的交通機能 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-25 滿意於清楚實用的租屋資訊
with st.expander("Q22-25.滿意於清楚實用的租屋資訊 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,84] ## 22-25滿意於清楚實用的租屋資訊
    column_index = 84
    item_name = "滿意於清楚實用的租屋資訊 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔



##### Q22-26 滿意於清楚實用的打工、獎助學金資訊
with st.expander("Q22-26.滿意於清楚實用的打工、獎助學金資訊 (範圍1～5；1為非常不滿意；5為非常滿意）:"):
    # df_freshman.iloc[:,85] ## 22-26滿意於清楚實用的打工、獎助學金資訊
    column_index = 85
    item_name = "滿意於清楚實用的打工、獎助學金資訊 (範圍1～5；1為非常不滿意；5為非常滿意）"
    column_title.append(df_freshman.columns[column_index][5:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔




###### Q23. 入學至今，對於課程安排的認同程度（範圍1～5；1為非常不同意；5為非常同意）
##### Q23-1 選課前，我可以在網站上清楚看到各課程大綱
with st.expander("Q23.入學至今，對於課程安排的認同程度. Q23-1.選課前，我可以在網站上清楚看到各課程大綱（範圍 1～5；1為非常不同意；5為非常同意）:"):
    # df_freshman.iloc[:,87] ## 23-1選課前，我可以在網站上清楚看到各課程大綱
    column_index = 87
    item_name = "選課前，我可以在網站上清楚看到各課程大綱（範圍 1～5；1為非常不同意；5為非常同意）"
    column_title.append(df_freshman.columns[column_index][1:])


    #### 產出 result_df
    result_df = Frequency_Distribution(df_freshman, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1)

    #### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  

    #### 使用Streamlit展示DataFrame "result_df"，但不显示索引
    # st.write(choice)
    st.write(f"<h6>{choice}</h6>", unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔

    #### 使用Streamlit畫單一圖 & 比較圖
    ### 畫比較圖時, 比較單位之選擇:
    if 院_系 == '0':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=[choice,'企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
    if 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=[choice,'資訊學院'],key=str(column_index)+'f')

    # Draw(院_系, column_index, ';', '沒有工讀', 1, result_df, selected_options, dataframes, combined_df)
    # Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df, selected_options)
    Draw(院_系, column_index, split_symbol=';', dropped_string='沒有工讀', sum_choice=1, result_df=result_df, selected_options=selected_options, dataframes=dataframes, combined_df=combined_df, width1=10,heigh1=6,width2=11,heigh2=8,width3=10,heigh3=6,title_fontsize=15,xlabel_fontsize = 14,ylabel_fontsize = 14,legend_fontsize = 14,xticklabel_fontsize = 14, yticklabel_fontsize = 14, annotation_fontsize = 14,bar_width = 0.2, fontsize_adjust=0)
    
st.markdown("##")  ## 更大的间隔
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
       





