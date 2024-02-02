# -*- coding: utf-8 -*-
"""
112學年度大二學習投入調查
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


@st.cache_data(ttl=3600, show_spinner="正在加載資料...")  ## Add the caching decorator
def load_data(path):
    df = pd.read_pickle(path)
    return df

@st.cache_data(ttl=3600, show_spinner="正在處理資料...")  ## Add the caching decorator
def Frequency_Distribution(df, column_index):
    ##### 将字符串按逗号分割并展平
    split_values = df.iloc[:,column_index].str.split(';').explode()
    ##### 去掉每一個字串前後的space
    split_values = split_values.str.strip()
    ##### 將以 '其他' 開頭的字串簡化為 '其他'
    split_values_np = np.where(split_values.str.startswith('其他'), '其他', split_values)
    split_values = pd.Series(split_values_np)  ## 轉換為 pandas.core.series.Series
    ##### 计算不同子字符串的出现次数
    value_counts = split_values.value_counts()
    ##### 计算不同子字符串的比例
    proportions = value_counts / value_counts.sum()
    ##### 轉換成 numpy array
    value_counts_numpy = value_counts.values
    proportions_numpy = proportions.values
    items_numpy = proportions.index.to_numpy()
    ##### 创建一个新的DataFrame来显示结果
    result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
    return result_df






#### 調整項目次序
###定义期望的項目顺序
### 函数：调整 DataFrame 以包含所有項目，且顺序正确
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





######  读取Pickle文件
df_freshman_original = load_data('df_freshman_original.pkl')
##### 使用rename方法更改column名称
df_freshman_original = df_freshman_original.rename(columns={'學系': '科系'})
# df_freshman_original = pd.read_pickle('df_freshman_original.pkl')
# df_freshman_original.shape  ## (1674, 186)
# df_freshman_original.index  ## RangeIndex(start=0, stop=1674, step=1)


####### 設定呈現標題 
html_temp = """
		<div style="background-color:#3872fb;padding:10px;border-radius:10px">
		<h1 style="color:white;text-align:center;"> 112大一新生學習適應調查 </h1>
		</div>
		"""
stc.html(html_temp)
st.markdown("##")  ## 更大的间隔



###### 預設定 df_freshman 以防止在等待選擇院系輸入時, 發生後面程式df_freshman讀不到資料而產生錯誤
choice='財金系' ##'化科系'
df_freshman = df_freshman_original[df_freshman_original['科系']==choice]
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
dataframes = [Frequency_Distribution(df, 7) for df in collections]  ## 22: "您工讀次要的原因為何:"
# len(dataframes)  ## 2
# len(dataframes[1]) ## 6
# len(dataframes[0]) ## 5


##### 形成所有學系'項目'欄位的所有值
desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
# desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 

##### 缺的項目值加以擴充， 並統一一樣的項目次序
dataframes = [adjust_df(df, desired_order) for df in dataframes]
# len(dataframes)  ## 2
# len(dataframes[0]) ## 6
# len(dataframes[1]) ## 6 
# dataframes[0]['項目']


combined_df = pd.concat(dataframes, keys=selected_options)
# combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])
# ''' 
#             項目  人數      比例
# 化科系 0  校內外獎助學金   1  0.0092
#     1    學雜費減免   9  0.0826
#     2     家庭提供  70  0.6422
#     3  打工或工讀所得   8  0.0734
#     4       其他   0  0.0000
#     5     助學貸款  21  0.1927
# 企管系 0  校內外獎助學金   1  0.0093
#     1    學雜費減免   3  0.0278
#     2     家庭提供  80  0.7407
#     3  打工或工讀所得   8  0.0741
#     4       其他   1  0.0093
#     5     助學貸款  15  0.1389
# '''





# st.subheader("以系或院進行查詢.u3vu4t86")
global 院_系
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


####### Q7 大學「學費」主要來源（可複選）
with st.expander("大學「學費」主要來源:"):
    # df_freshman.iloc[:,7] ## 7大學「學費」主要來源（可複選）
    column_index = 7
    item_name = "大學「學費」主要來源"
    column_title.append(df_freshman.columns[column_index][2:])
    result_df = Frequency_Distribution(df_freshman, column_index)
    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  


    ##### 使用Streamlit展示DataFrame，但不显示索引
    # st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔


    ##### 使用Streamlit畫單一圖
    # st.markdown(f"圖形中項目(由下至上): {result_df['項目'].values.tolist()}")
    if 院_系 == '0':
        collections = [df_freshman, df_freshman_faculty, df_freshman_original]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
        desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

        #### 設置 matplotlib 支持中文的字體: 
        # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
        # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        #### 设置条形的宽度
        bar_width = 0.2
        #### 设置x轴的位置
        r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
        #### 设置字体大小
        title_fontsize = 15
        xlabel_fontsize = 14
        ylabel_fontsize = 14
        xticklabel_fontsize = 14
        annotation_fontsize = 8
        legend_fontsize = 14
        #### 绘制条形
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
            # 计算当前分组的条形数量
            num_bars = len(df)
            # 生成当前分组的x轴位置
            index = np.arange(num_bars) + i * bar_width
            # index = r + i * bar_width
            rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
            # # 在每个条形上标示比例
            # for rect, ratio in zip(rects, df['比例']):
            #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
        ### 添加图例
        ax.legend(fontsize=legend_fontsize)
        ### 添加x轴标签
        ## 计算每个组的中心位置作为x轴刻度位置
        # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
        # group_centers = np.arange(len(dataframes[0]))
        ## 添加x轴标签
        # ax.set_xticks(group_centers)
        # dataframes[0]['項目'].values
        # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
        ax.set_xticks(r + bar_width * (len(dataframes) / 2))
        ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
        # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
        ### 设置标题和轴标签
        ax.set_title(item_name,fontsize=title_fontsize)
        # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
        ax.set_ylabel('比例',fontsize=ylabel_fontsize)
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
        plt.barh(result_df['項目'], result_df['人數'], label=choice)
        #### 標示比例數據
        for i in range(len(result_df['項目'])):
            plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
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
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
        collections = [df_freshman_original[df_freshman_original['科系']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=selected_options)
    elif 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=['理學','資訊'],key=str(column_index)+'f')
        collections = [df_freshman_original[df_freshman_original['學院']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]        
        combined_df = pd.concat(dataframes, keys=selected_options)
        
    #### 設置 matplotlib 支持中文的字體: 
    # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
    # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
    matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    #### 设置条形的宽度
    bar_width = 0.2
    #### 设置x轴的位置
    r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
    #### 设置字体大小
    title_fontsize = 15
    xlabel_fontsize = 14
    ylabel_fontsize = 14
    xticklabel_fontsize = 14
    annotation_fontsize = 8
    legend_fontsize = 14
    #### 绘制条形
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
        # 计算当前分组的条形数量
        num_bars = len(df)
        # 生成当前分组的x轴位置
        index = np.arange(num_bars) + i * bar_width
        # index = r + i * bar_width
        rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

        # # 在每个条形上标示比例
        # for rect, ratio in zip(rects, df['比例']):
        #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
    ### 添加图例
    ax.legend(fontsize=legend_fontsize)
    ### 添加x轴标签
    ## 计算每个组的中心位置作为x轴刻度位置
    # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
    # group_centers = np.arange(len(dataframes[0]))
    ## 添加x轴标签
    # ax.set_xticks(group_centers)
    # dataframes[0]['項目'].values
    # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
    ax.set_xticks(r + bar_width * (len(dataframes) / 2))
    ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
    # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
    ### 设置标题和轴标签
    ax.set_title(item_name,fontsize=title_fontsize)
    # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
    ax.set_ylabel('比例',fontsize=ylabel_fontsize)
    ### 显示网格线
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.tight_layout()
    # plt.show()
    ### 在Streamlit中显示
    st.pyplot(plt)

st.markdown("##")  ## 更大的间隔    




####### Q8 學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源
with st.expander("學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源:"):
    # df_freshman.iloc[:,8] ## 8學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源（可複選）
    column_index = 8
    item_name = "學習及生活費（書籍、住宿、交通、伙食等開銷）主要來源"
    column_title.append(df_freshman.columns[column_index][2:])
    result_df = Frequency_Distribution(df_freshman, column_index)
    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  


    ##### 使用Streamlit展示DataFrame，但不显示索引
    # st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔


    ##### 使用Streamlit畫單一圖
    # st.markdown(f"圖形中項目(由下至上): {result_df['項目'].values.tolist()}")
    if 院_系 == '0':
        collections = [df_freshman, df_freshman_faculty, df_freshman_original]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
        desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

        #### 設置 matplotlib 支持中文的字體: 
        # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
        # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        #### 设置条形的宽度
        bar_width = 0.2
        #### 设置x轴的位置
        r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
        #### 设置字体大小
        title_fontsize = 15
        xlabel_fontsize = 14
        ylabel_fontsize = 14
        xticklabel_fontsize = 14
        annotation_fontsize = 8
        legend_fontsize = 14
        #### 绘制条形
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
            # 计算当前分组的条形数量
            num_bars = len(df)
            # 生成当前分组的x轴位置
            index = np.arange(num_bars) + i * bar_width
            # index = r + i * bar_width
            rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
            # # 在每个条形上标示比例
            # for rect, ratio in zip(rects, df['比例']):
            #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
        ### 添加图例
        ax.legend(fontsize=legend_fontsize)
        ### 添加x轴标签
        ## 计算每个组的中心位置作为x轴刻度位置
        # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
        # group_centers = np.arange(len(dataframes[0]))
        ## 添加x轴标签
        # ax.set_xticks(group_centers)
        # dataframes[0]['項目'].values
        # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
        ax.set_xticks(r + bar_width * (len(dataframes) / 2))
        ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
        # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
        ### 设置标题和轴标签
        ax.set_title(item_name,fontsize=title_fontsize)
        # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
        ax.set_ylabel('比例',fontsize=ylabel_fontsize)
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
        plt.barh(result_df['項目'], result_df['人數'], label=choice)
        #### 標示比例數據
        for i in range(len(result_df['項目'])):
            plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
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
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
        collections = [df_freshman_original[df_freshman_original['科系']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=selected_options)
    elif 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=['理學','資訊'],key=str(column_index)+'f')
        collections = [df_freshman_original[df_freshman_original['學院']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]        
        combined_df = pd.concat(dataframes, keys=selected_options)
        
    #### 設置 matplotlib 支持中文的字體: 
    # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
    # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
    matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    #### 设置条形的宽度
    bar_width = 0.2
    #### 设置x轴的位置
    r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
    #### 设置字体大小
    title_fontsize = 15
    xlabel_fontsize = 14
    ylabel_fontsize = 14
    xticklabel_fontsize = 14
    annotation_fontsize = 8
    legend_fontsize = 14
    #### 绘制条形
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
        # 计算当前分组的条形数量
        num_bars = len(df)
        # 生成当前分组的x轴位置
        index = np.arange(num_bars) + i * bar_width
        # index = r + i * bar_width
        rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

        # # 在每个条形上标示比例
        # for rect, ratio in zip(rects, df['比例']):
        #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
    ### 添加图例
    ax.legend(fontsize=legend_fontsize)
    ### 添加x轴标签
    ## 计算每个组的中心位置作为x轴刻度位置
    # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
    # group_centers = np.arange(len(dataframes[0]))
    ## 添加x轴标签
    # ax.set_xticks(group_centers)
    # dataframes[0]['項目'].values
    # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
    ax.set_xticks(r + bar_width * (len(dataframes) / 2))
    ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
    # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
    ### 设置标题和轴标签
    ax.set_title(item_name,fontsize=title_fontsize)
    # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
    ax.set_ylabel('比例',fontsize=ylabel_fontsize)
    ### 显示网格线
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.tight_layout()
    # plt.show()
    ### 在Streamlit中显示
    st.pyplot(plt)

st.markdown("##")  ## 更大的间隔    





####### Q9 我的入學管道
with st.expander("我的入學管道:"):
    # df_freshman.iloc[:,9] ## 9我的入學管道
    column_index = 9
    item_name = "我的入學管道"
    column_title.append(df_freshman.columns[column_index][2:])
    result_df = Frequency_Distribution(df_freshman, column_index)
    ##### 存到 list 'df_streamlit'
    df_streamlit.append(result_df)  


    ##### 使用Streamlit展示DataFrame，但不显示索引
    # st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
    st.write(result_df.to_html(index=False), unsafe_allow_html=True)
    st.markdown("##")  ## 更大的间隔


    ##### 使用Streamlit畫單一圖
    # st.markdown(f"圖形中項目(由下至上): {result_df['項目'].values.tolist()}")
    if 院_系 == '0':
        collections = [df_freshman, df_freshman_faculty, df_freshman_original]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
        desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

        #### 設置 matplotlib 支持中文的字體: 
        # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
        # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        #### 设置条形的宽度
        bar_width = 0.2
        #### 设置x轴的位置
        r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
        #### 设置字体大小
        title_fontsize = 15
        xlabel_fontsize = 14
        ylabel_fontsize = 14
        xticklabel_fontsize = 14
        annotation_fontsize = 8
        legend_fontsize = 14
        #### 绘制条形
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
            # 计算当前分组的条形数量
            num_bars = len(df)
            # 生成当前分组的x轴位置
            index = np.arange(num_bars) + i * bar_width
            # index = r + i * bar_width
            rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
            # # 在每个条形上标示比例
            # for rect, ratio in zip(rects, df['比例']):
            #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
        ### 添加图例
        ax.legend(fontsize=legend_fontsize)
        ### 添加x轴标签
        ## 计算每个组的中心位置作为x轴刻度位置
        # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
        # group_centers = np.arange(len(dataframes[0]))
        ## 添加x轴标签
        # ax.set_xticks(group_centers)
        # dataframes[0]['項目'].values
        # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
        ax.set_xticks(r + bar_width * (len(dataframes) / 2))
        ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
        # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
        ### 设置标题和轴标签
        ax.set_title(item_name,fontsize=title_fontsize)
        # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
        ax.set_ylabel('比例',fontsize=ylabel_fontsize)
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
        plt.barh(result_df['項目'], result_df['人數'], label=choice)
        #### 標示比例數據
        for i in range(len(result_df['項目'])):
            plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
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
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學系：', df_freshman_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
        collections = [df_freshman_original[df_freshman_original['科系']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]
        combined_df = pd.concat(dataframes, keys=selected_options)
    elif 院_系 == '1':
        ## 使用multiselect组件让用户进行多重选择
        selected_options = st.multiselect('選擇比較學院：', df_freshman_original['學院'].unique(), default=['理學','資訊'],key=str(column_index)+'f')
        collections = [df_freshman_original[df_freshman_original['學院']==i] for i in selected_options]
        dataframes = [Frequency_Distribution(df, column_index) for df in collections]
        ## 形成所有學系'項目'欄位的所有值
        desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
        ## 缺的項目值加以擴充， 並統一一樣的項目次序
        dataframes = [adjust_df(df, desired_order) for df in dataframes]        
        combined_df = pd.concat(dataframes, keys=selected_options)
        
    #### 設置 matplotlib 支持中文的字體: 
    # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
    # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
    matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    #### 设置条形的宽度
    bar_width = 0.2
    #### 设置x轴的位置
    r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
    #### 设置字体大小
    title_fontsize = 15
    xlabel_fontsize = 14
    ylabel_fontsize = 14
    xticklabel_fontsize = 11
    annotation_fontsize = 8
    legend_fontsize = 14
    #### 绘制条形
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
        # 计算当前分组的条形数量
        num_bars = len(df)
        # 生成当前分组的x轴位置
        index = np.arange(num_bars) + i * bar_width
        # index = r + i * bar_width
        # rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
        rects = ax.barh(index, df['比例'], height=bar_width, label=college_name)

        # # 在每个条形上标示比例
        # for rect, ratio in zip(rects, df['比例']):
        #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
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
    # ## 调整x轴刻度标签的偏斜程度
    # plt.xticks(rotation=45)  # 以45度角倾斜刻度标签，您可以根据需要调整这个角度

    ### 设置y轴刻度标签
    ax.set_yticks(r + bar_width*(len(dataframes) / 2))  # 调整位置以使标签居中对齐到每个条形
    ax.set_yticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)


    ### 设置标题和轴标签
    ax.set_title(item_name,fontsize=title_fontsize)
    # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
    ax.set_ylabel('比例',fontsize=ylabel_fontsize)
    ### 显示网格线
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
    plt.tight_layout()
    # plt.show()

    ### 在Streamlit中显示
    st.pyplot(plt)

st.markdown("##")  ## 更大的间隔    












# # ###### Part1-2 您的大一專業基礎課程學習情況，學習良好的課程名稱請以「,」隔開，如無，請填「無」
# # #df_sophomore.columns
# # df_sophomore.iloc[:,8] ## 2.您的大一專業基礎課程學習情況，學習良好的課程名稱請以「,」隔開，如無，請填「無」

# # ##### 按'科系'分组，然后将 '2.您的大一專業基礎課程學習情況，學習良好的課程名稱請以「,」隔開，如無，請填「無」' 此行的字符串按逗号分割并展平
# # split_values = df_sophomore.groupby('科系')['2.您的大一專業基礎課程學習情況，學習良好的課程名稱請以「,」隔開，如無，請填「無」'].apply(lambda x: x.str.split(',| |，').explode())
# # ##### 计算每个科系內部中不同子字符串的出现次数
# # counts = split_values.groupby(level=0).value_counts()
# # #type(counts)  ## pandas.core.series.Series
# # ##### 更改 series 的 index 欄位名稱
# # counts.index.names = ['科系', '學習良好課程']

# # #%% (三) 以下
# # print(counts)
# # '''
# # 科系   學習良好課程    
# # 中文系  無             27
# #       文學概論           8
# #       語言學概論          7
# #       兒童文學概論         5
# #       國學導讀           4
# #                     ..
# # 食營系  食品基礎分析化學實驗     1
# #       食品基礎分析實驗       1
# #       食品工程           1
# #       食物製備           1
# #       食物製備實驗         1
# # Name: 2.您的大一專業基礎課程學習情況，學習良好的課程名稱請以「,」隔開，如無，請填「無」, Length: 590, dtype: int64
# # '''
# # ##### 将 MultiIndex Series 'counts' 转换为DataFrame
# # #### 將 兩個index 變columns
# # counts_df = counts.reset_index()
# # #### 將新的兩個columns 重新命名
# # counts_df.columns = ['科系', '學習良好課程', '人數']
# # print(counts_df)
# # '''
# #       科系      學習良好課程  人數
# # 0    中文系           無  27
# # 1    中文系        文學概論   8
# # 2    中文系       語言學概論   7
# # 3    中文系      兒童文學概論   5
# # 4    中文系        國學導讀   4
# # ..   ...         ...  ..
# # 585  食營系  食品基礎分析化學實驗   1
# # 586  食營系    食品基礎分析實驗   1
# # 587  食營系        食品工程   1
# # 588  食營系        食物製備   1
# # 589  食營系      食物製備實驗   1

# # [590 rows x 3 columns]
# # '''
# # counts_df.to_excel(r'C:\Users\user\Dropbox\系務\校務研究IR\大二學生學習投入問卷調查分析\112\各學系大一學習良好課程.xlsx', index=False, engine='openpyxl')
# # #%% (三) 以上


# # ###### Part1-3 您的大一專業基礎課程學習情況，學習不良的課程名稱請以「,」隔開，如無，請填「無」
# # #df_sophomore.columns
# # df_sophomore.iloc[:,9] ## 3.您的大一專業基礎課程學習情況，學習不良的課程名稱請以「,」隔開，如無，請填「無」
# # ##### 按'科系'分组，然后将 '3.您的大一專業基礎課程學習情況，學習不良的課程名稱請以「,」隔開，如無，請填「無」' 此行的字符串按逗号空格分割并展平
# # split_values = df_sophomore.groupby('科系')['3.您的大一專業基礎課程學習情況，學習不良的課程名稱請以「,」隔開，如無，請填「無」'].apply(lambda x: x.str.split(',| |，').explode())
# # ##### 计算每个科系內部中不同子字符串的出现次数
# # counts = split_values.groupby(level=0).value_counts()
# # #type(counts)  ## pandas.core.series.Series
# # ##### 更改 series 的 index 欄位名稱
# # counts.index.names = ['科系', '學習不良課程']

# # #%% (四) 以下
# # print(counts)
# # '''
# # 科系   學習不良課程  
# # 中文系  無           39
# #      文學概論         4
# #      英文           3
# #      語言學概論        3
# #      台灣原住民族文化     1
# #                  ..
# # 食營系  程式設計         1
# #      英文           1
# #      食品分析化學       1
# #      食品基礎分析化學     1
# #      食客記趣         1
# # Name: 3.您的大一專業基礎課程學習情況，學習不良的課程名稱請以「,」隔開，如無，請填「無」, Length: 375, dtype: int64
# # '''
# # ##### 将 MultiIndex Series 'counts' 转换为DataFrame
# # #### 將 兩個index 變columns
# # counts_df = counts.reset_index()
# # #### 將新的兩個columns 重新命名
# # counts_df.columns = ['科系', '學習不良課程', '人數']
# # print(counts_df)
# # '''
# #       科系    學習不良課程  人數
# # 0    中文系         無  39
# # 1    中文系      文學概論   4
# # 2    中文系        英文   3
# # 3    中文系     語言學概論   3
# # 4    中文系  台灣原住民族文化   1
# # ..   ...       ...  ..
# # 370  食營系      程式設計   1
# # 371  食營系        英文   1
# # 372  食營系    食品分析化學   1
# # 373  食營系  食品基礎分析化學   1
# # 374  食營系      食客記趣   1

# # [375 rows x 3 columns]
# # '''
# # counts_df.to_excel(r'C:\Users\user\Dropbox\系務\校務研究IR\大二學生學習投入問卷調查分析\112\各學系大一學習不良課程.xlsx', index=False, engine='openpyxl')
# # #%% (四) 以上


# ###### Part1-4 大學畢業後的規劃
# with st.expander("大學畢業後的規劃:"):
#     #df_sophomore.columns
#     # df_sophomore.iloc[:,10] ## 4. 大學畢業後的規劃
#     column_index = 10
#     item_name = "大學畢業後的規劃:"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  



#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     # st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.write(result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index)+'f')
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
  
#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔    



# ###### Part1-5 學習及生活費(書籍、住宿、交通、伙食等開銷) 主要來源。
# with st.expander("學習及生活費(書籍、住宿、交通、伙食等開銷) 主要來源:"):
#     # df_sophomore.columns
#     # df_sophomore.iloc[:,11] ## 5. 學習及生活費(書籍、住宿、交通、伙食等開銷) 主要來源。
#     column_index = 11
#     item_name = "學習及生活費(書籍、住宿、交通、伙食等開銷) 主要來源:"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     # st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.write(result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index)+'d')  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index)+'f')
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔    





# ####### Part2  時間規劃
# ###### Part2-6 您二年級就學期間是否工讀 ?
# with st.expander("您二年級就學期間是否工讀:"):
#     # df_sophomore.iloc[:,18] ## 6. 您二年級就學期間是否工讀?
#     column_index = 18
#     item_name = "您二年級就學期間是否工讀:"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     # st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.write(result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)


# st.markdown("##")  ## 更大的间隔    






# ###### Part2-7 您二年級「上學期」平均每周工讀時數 ?
# with st.expander("您二年級「上學期」平均每周工讀時數:"):
#     # df_sophomore.iloc[:,19] ## 7.您二年級「上學期」平均每周工讀時數 ?
#     column_index = 19
#     item_name = "您二年級「上學期」平均每周工讀時數:"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)



#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     # ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     # ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticks(np.arange(num_bars) + bar_width * (len(dataframes) / 2))
#     # ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ax.set_xticklabels(df['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)


# st.markdown("##")  ## 更大的间隔    





# ###### Part2-8 您二年級「上學期」的工讀地點為何 ?
# with st.expander("您二年級「上學期」的工讀地點為何:"):
#     # df_sophomore.iloc[:,20] ## 8.您二年級「上學期」的工讀地點為何 ?
#     column_index = 20
#     item_name = "您二年級「上學期」的工讀地點為何"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔    



# ###### Part2-9  您工讀最主要的原因為何?
# with st.expander("您工讀最主要的原因為何:"):
#     # df_sophomore.iloc[:,21] ##  9.您工讀最主要的原因為何?
#     column_index = 21
#     item_name = "您工讀最主要的原因為何"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 11
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)


# st.markdown("##")  ## 更大的间隔    




# ###### Part2-10  您工讀次要的原因為何?
# with st.expander("您工讀次要的原因為何:"):
#     # df_sophomore.iloc[:,22] ##  10.您工讀次要的原因為何?
#     column_index = 22
#     item_name = "您工讀次要的原因為何"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 11
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔   






# ###### Part2-11 您每周平均上網時間為何?
# with st.expander("您每周平均上網時間為何:"):
#     # df_sophomore.iloc[:,23] ##  11.您每周平均上網時間為何?
#     column_index = 23
#     item_name = "您每周平均上網時間為何"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔   






# ###### Part2-12 您上網主要用途為何? (最主要用途)
# with st.expander("您上網主要用途為何:"):
#     # df_sophomore.iloc[:,24] ##  12.您上網主要用途為何? (最主要用途)
#     column_index = 24
#     item_name = "您上網主要用途為何"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔   







# ###### Part2-13 您上網次要用途為何? (次要用途)
# with st.expander("您上網次要用途為何:"):
#     # df_sophomore.iloc[:,25] ##  13.您上網次要用途為何? (次要用途)
#     column_index = 25
#     item_name = "您上網次要用途為何"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔   



# ###### Part2-14 除了上課時間外，您每天平均念書的時間為何?
# with st.expander("除了上課時間外，您每天平均念書的時間為何:"):
#     # df_sophomore.iloc[:,26] ##  14.除了上課時間外，您每天平均念書的時間為何?
#     column_index = 26
#     item_name = "除了上課時間外，您每天平均念書的時間為何"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 14
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔   






# ####### Part3  學習投入 (依多數課程情況回答)
# ###### Part3-1 學習投入 (依多數課程情況回答): 上課時我
# with st.expander("學習投入 (依多數課程情況回答): 上課時我:"):
#     # df_sophomore.iloc[:,28] ##  學習投入 (依多數課程情況回答): 上課時我
#     column_index = 28
#     item_name = "學習投入 (依多數課程情況回答): 上課時我:"
#     column_title.append(df_sophomore.columns[column_index][2:])
#     ##### 将字符串按逗号分割并展平
#     split_values = df_sophomore.iloc[:,column_index].str.split(',').explode()
#     ##### 计算不同子字符串的出现次数
#     value_counts = split_values.value_counts()
#     ##### 计算不同子字符串的比例
#     proportions = value_counts / value_counts.sum()
#     ##### 轉換成 numpy array
#     value_counts_numpy = value_counts.values
#     proportions_numpy = proportions.values
#     items_numpy = proportions.index.to_numpy()
#     ##### 创建一个新的DataFrame来显示结果
#     result_df = pd.DataFrame({'項目':items_numpy, '人數': value_counts_numpy,'比例': proportions_numpy.round(4)})
#     ##### 存到 list 'df_streamlit'
#     df_streamlit.append(result_df)  


#     ##### 使用Streamlit展示DataFrame，但不显示索引
#     st.write(item_name, result_df.to_html(index=False), unsafe_allow_html=True)
#     st.markdown("##")  ## 更大的间隔


#     ##### 使用Streamlit畫單一圖
#     if 院_系 == '0':
#         collections = [df_sophomore, df_sophomore_faculty, df_sophomore_original]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         # desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()]))
#         desired_order  = list(set([item for item in dataframes[0]['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=[choice,choice_faculty,'全校'])

#         #### 設置 matplotlib 支持中文的字體: 
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 设置条形的宽度
#         bar_width = 0.2
#         #### 设置x轴的位置
#         r = np.arange(len(dataframes[0]))  ## len(result_df_理學_rr)=6, 因為result_df_理學_rr 有 6個 row: 非常滿意, 滿意, 普通, 不滿意, 非常不滿意
#         #### 设置字体大小
#         title_fontsize = 15
#         xlabel_fontsize = 14
#         ylabel_fontsize = 14
#         xticklabel_fontsize = 14
#         annotation_fontsize = 8
#         legend_fontsize = 14
#         #### 绘制条形
#         fig, ax = plt.subplots(figsize=(10, 6))
#         for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#             # 计算当前分组的条形数量
#             num_bars = len(df)
#             # 生成当前分组的x轴位置
#             index = np.arange(num_bars) + i * bar_width
#             # index = r + i * bar_width
#             rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)
    
#             # # 在每个条形上标示比例
#             # for rect, ratio in zip(rects, df['比例']):
#             #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#         ### 添加图例
#         ax.legend(fontsize=legend_fontsize)
#         ### 添加x轴标签
#         ## 计算每个组的中心位置作为x轴刻度位置
#         # group_centers = r + bar_width * (num_colleges / 2 - 0.5)
#         # group_centers = np.arange(len(dataframes[0]))
#         ## 添加x轴标签
#         # ax.set_xticks(group_centers)
#         # dataframes[0]['項目'].values
#         # "array(['個人興趣', '未來能找到好工作', '落點分析', '沒有特定理由', '家人的期望與建議', '師長推薦'],dtype=object)"
#         ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#         ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#         # ax.set_xticklabels(['非常滿意', '滿意', '普通', '不滿意','非常不滿意'],fontsize=xticklabel_fontsize)
#         ### 设置标题和轴标签
#         ax.set_title(item_name,fontsize=title_fontsize)
#         # ax.set_xlabel('满意度',fontsize=xlabel_fontsize)
#         ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#         ### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         plt.tight_layout()
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)

#     if 院_系 == '1':
#         #### 設置中文顯示
#         # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#         # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#         matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#         matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#         #### 创建图形和坐标轴
#         plt.figure(figsize=(11, 8))
#         #### 绘制条形图
#         plt.barh(result_df['項目'], result_df['人數'], label=choice)
#         #### 標示比例數據
#         for i in range(len(result_df['項目'])):
#             plt.text(result_df['人數'][i]+1, result_df['項目'][i], f'{result_df.iloc[:, 2][i]:.0%}', fontsize=14)
#         #### 添加一些图形元素
#         plt.title(item_name, fontsize=15)
#         plt.xlabel('人數', fontsize=14)
#         #plt.ylabel('本校現在所提供的資源或支援事項')
#         #### 调整x轴和y轴刻度标签的字体大小
#         plt.tick_params(axis='both', labelsize=14)  # 同时调整x轴和y轴
#         plt.legend(fontsize=14)
#         #### 显示网格线
#         plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#         #### 显示图形
#         ### 一般顯示
#         # plt.show()
#         ### 在Streamlit中显示
#         st.pyplot(plt)


#     ##### 使用streamlit 畫比較圖
#     if 院_系 == '0':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學系：', df_sophomore_original['科系'].unique(), default=['化科系','企管系'],key=str(column_index))  ## # selected_options = ['化科系','企管系']
#         collections = [df_sophomore_original[df_sophomore_original['科系']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)
#     elif 院_系 == '1':
#         ## 使用multiselect组件让用户进行多重选择
#         selected_options = st.multiselect('選擇比較學院：', df_sophomore_original['學院'].unique(), default=['理學院','資訊學院'],key=str(column_index))
#         collections = [df_sophomore_original[df_sophomore_original['學院']==i] for i in selected_options]
#         dataframes = [Frequency_Distribution(df, column_index) for df in collections]
#         ## 形成所有學系'項目'欄位的所有值
#         desired_order  = list(set([item for df in dataframes for item in df['項目'].tolist()])) 
#         ## 缺的項目值加以擴充， 並統一一樣的項目次序
#         dataframes = [adjust_df(df, desired_order) for df in dataframes]
#         combined_df = pd.concat(dataframes, keys=selected_options)

#     #### 設置 matplotlib 支持中文的字體: 
#     # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
#     # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
#     matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'
#     matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#     #### 设置条形的宽度
#     bar_width = 0.2
#     #### 设置x轴的中心位置
#     r = np.arange(len(dataframes[0]))  ## 
#     #### 设置字体大小
#     title_fontsize = 15
#     xlabel_fontsize = 14
#     ylabel_fontsize = 14
#     xticklabel_fontsize = 11
#     annotation_fontsize = 8
#     legend_fontsize = 14
#     #### 绘制条形
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for i, (college_name, df) in enumerate(combined_df.groupby(level=0)):
#         # 计算当前分组的条形数量
#         num_bars = len(df)
#         # 生成当前分组的x轴位置
#         index = np.arange(num_bars) + i * bar_width
#         # index = r + i * bar_width
#         rects = ax.bar(index, df['比例'], width=bar_width, label=college_name)

#         # # 在每个条形上标示比例
#         # for rect, ratio in zip(rects, df['比例']):
#         #     ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'{ratio:.2%}', ha='center', va='bottom',fontsize=annotation_fontsize)
#     ### 添加图例
#     ax.legend(fontsize=legend_fontsize)
#     ### 添加x轴标签
#     ## 计算每个组的中心位置r作为x轴刻度位置
#     ax.set_xticks(r + bar_width * (len(dataframes) / 2))
#     ax.set_xticklabels(dataframes[0]['項目'].values, fontsize=xticklabel_fontsize)
#     ### 设置标题和轴标签
#     ax.set_title(item_name,fontsize=title_fontsize)
#     # ax.set_xlabel('項目',fontsize=xlabel_fontsize)
#     ax.set_ylabel('比例',fontsize=ylabel_fontsize)
#     ### 显示网格线
#     plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
#     plt.tight_layout()
#     # plt.show()
#     ### 在Streamlit中显示
#     st.pyplot(plt)

# st.markdown("##")  ## 更大的间隔   






# # ####### Part4  學校學習環境滿意度
# # ###### Part4-1 儀器設備
# # df_sophomore.iloc[:,30] ##  1.儀器設備
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,28].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,30].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (十六) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('儀器設備滿意度:')
# # print(result_df)
# # '''
# # 儀器設備滿意度:
# #        人數     比例
# # 普通   1133  0.618
# # 滿意    601  0.328
# # 不滿意    88  0.048
# # 不適用    12  0.007
# # '''
# # #### 將 index 變column
# # result_df_儀器設備 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_儀器設備.rename(columns={'index': '儀器設備滿意度'}, inplace=True)
# # print(result_df_儀器設備)

# # '''
# #   儀器設備滿意度    人數     比例
# # 0      普通  1133  0.618
# # 1      滿意   601  0.328
# # 2     不滿意    88  0.048
# # 3     不適用    12  0.007
# # '''
# # #%% (十六) 以上


# # ###### Part4-2 實驗器材
# # df_sophomore.iloc[:,31] ##  2.實驗器材
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,28].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,31].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (十七) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('實驗器材滿意度:')
# # print(result_df)
# # # '''
# # # 實驗器材滿意度:
# # #        人數     比例
# # # 普通   1172  0.639
# # # 滿意    502  0.274
# # # 不適用   114  0.062
# # # 不滿意    46  0.025
# # # '''
# # #### 將 index 變column
# # result_df_實驗器材 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_實驗器材.rename(columns={'index': '實驗器材滿意度'}, inplace=True)
# # print(result_df_實驗器材)

# # # '''
# # #   實驗器材滿意度    人數     比例
# # # 0      普通  1172  0.639
# # # 1      滿意   502  0.274
# # # 2     不適用   114  0.062
# # # 3     不滿意    46  0.025
# # # '''

# # #### 調換 '不適用' 與 '不滿意' 的 index 順序, 因為要與其他滿意度的圖項目一致
# # result_df_實驗器材_reindexed = result_df_實驗器材.reindex([0,1,3,2])
# # result_df_實驗器材_reindexed = result_df_實驗器材_reindexed.reset_index(drop=True)  ## 重設 index
# # print(result_df_實驗器材_reindexed)
# # '''
# #   實驗器材滿意度    人數     比例
# # 0      普通  1172  0.639
# # 1      滿意   502  0.274
# # 2     不滿意    46  0.025
# # 3     不適用   114  0.062
# # '''
# # #%% (十七) 以上


# # ###### Part4-3 教室空間
# # df_sophomore.iloc[:,32] ##  3.教室空間
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,28].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,32].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (十八) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('教室空間滿意度:')
# # print(result_df)
# # '''
# # 教室空間滿意度:
# #        人數     比例
# # 普通   1047  0.571
# # 滿意    633  0.345
# # 不滿意   146  0.080
# # 不適用     8  0.004
# # '''
# # #### 將 index 變column
# # result_df_教室空間 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_教室空間.rename(columns={'index': '教室空間滿意度'}, inplace=True)
# # print(result_df_教室空間)

# # '''
# #   教室空間滿意度    人數     比例
# # 0      普通  1047  0.571
# # 1      滿意   633  0.345
# # 2     不滿意   146  0.080
# # 3     不適用     8  0.004
# # '''
# # #%% (十八) 以上


# # ###### Part4-4 教室環境
# # df_sophomore.iloc[:,33] ##  4.教室環境
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,28].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,32].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (十九) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('教室環境滿意度:')
# # print(result_df)
# # '''
# # 教室環境滿意度:
# #        人數     比例
# # 普通   1047  0.571
# # 滿意    633  0.345
# # 不滿意   146  0.080
# # 不適用     8  0.004
# # '''
# # #### 將 index 變column
# # result_df_教室環境 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_教室環境.rename(columns={'index': '教室環境滿意度'}, inplace=True)
# # print(result_df_教室環境)

# # '''
# #   教室環境滿意度    人數     比例
# # 0      普通  1047  0.571
# # 1      滿意   633  0.345
# # 2     不滿意   146  0.080
# # 3     不適用     8  0.004
# # '''
# # #%% (十九) 以上


# # ###### Part4-5 自學空間
# # df_sophomore.iloc[:,34] ##  5.自學空間
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,28].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,34].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二十) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('自學空間滿意度:')
# # print(result_df)
# # '''
# # 自學空間滿意度:
# #       人數     比例
# # 普通   944  0.515
# # 滿意   828  0.451
# # 不滿意   43  0.023
# # 不適用   19  0.010
# # '''
# # #### 將 index 變column
# # result_df_自學空間 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_自學空間.rename(columns={'index': '自學空間滿意度'}, inplace=True)
# # print(result_df_自學空間)

# # '''
# #    自學空間滿意度   人數     比例
# #  0      普通  944  0.515
# #  1      滿意  828  0.451
# #  2     不滿意   43  0.023
# #  3     不適用   19  0.010
# # '''
# # #%% (二十) 以上


# # ###### Part4-6 學校宿舍
# # df_sophomore.iloc[:,35] ##  6.學校宿舍
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,28].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,35].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二一) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('學校宿舍滿意度:')
# # print(result_df)
# # # '''
# # # 學校宿舍滿意度:
# # #       人數     比例
# # # 普通   907  0.495
# # # 滿意   514  0.280
# # # 不適用  213  0.116
# # # 不滿意  200  0.109
# # # '''
# # #### 將 index 變column
# # result_df_學校宿舍 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_學校宿舍.rename(columns={'index': '學校宿舍滿意度'}, inplace=True)
# # print(result_df_學校宿舍)

# # # '''
# # #   學校宿舍滿意度   人數     比例
# # # 0      普通  907  0.495
# # # 1      滿意  514  0.280
# # # 2     不適用  213  0.116
# # # 3     不滿意  200  0.109
# # # '''
# # #### 調換 '不適用' 與 '不滿意' 的 index 順序, 因為要與其他滿意度的圖項目一致
# # result_df_學校宿舍_reindexed = result_df_學校宿舍.reindex([0,1,3,2])
# # result_df_學校宿舍_reindexed = result_df_學校宿舍_reindexed.reset_index(drop=True)  ## 重設 index
# # print(result_df_學校宿舍_reindexed)
# # '''
# #   學校宿舍滿意度   人數     比例
# # 0      普通  907  0.495
# # 1      滿意  514  0.280
# # 2     不滿意  200  0.109
# # 3     不適用  213  0.116
# # '''
# # #%% (二一) 以上


# # ###### Part4-7 校園網路
# # df_sophomore.iloc[:,36] ##  7.校園網路
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,28].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,36].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二二) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('校園網路滿意度:')
# # print(result_df)
# # '''
# # 校園網路滿意度:
# #       人數     比例
# # 普通   932  0.508
# # 滿意   519  0.283
# # 不滿意  344  0.188
# # 不適用   39  0.021
# # '''
# # #### 將 index 變column
# # result_df_校園網路 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_校園網路.rename(columns={'index': '校園網路滿意度'}, inplace=True)
# # print(result_df_校園網路)

# # '''
# #   校園網路滿意度   人數     比例
# # 0      普通  932  0.508
# # 1      滿意  519  0.283
# # 2     不滿意  344  0.188
# # 3     不適用   39  0.021
# # '''
# # #%% (二二) 以上


# # #%% (二二圖) 以下
# # ###### 畫圖: 學校學習環境滿意度
# # ##### 创建一个 3x3 的子图布局
# # fig, axes = plt.subplots(3, 3, figsize=(11, 8))

# # #### 儀器設備 滿意度条形图
# # axes[0,0].bar(result_df_儀器設備.iloc[:,0], result_df_儀器設備.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_儀器設備.iloc[:,0])):
# #     axes[0,0].text(result_df_儀器設備.iloc[:,0][i], result_df_儀器設備.iloc[:,1][i]+15, f'{result_df_儀器設備.iloc[:, 2][i]:.2%}', fontsize=10)
# # ### 添加一些图形元素
# # axes[0, 0].set_title('儀器設備滿意度', fontsize=12)
# # #axes[0, 0].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[0, 0].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[0, 0].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 實驗器材 滿意度条形图result_df_學校宿舍_reindexed
# # axes[0, 1].bar(result_df_實驗器材_reindexed.iloc[:,0], result_df_實驗器材_reindexed.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_實驗器材_reindexed.iloc[:,0])):
# #     if i==3:
# #         axes[0, 1].text(result_df_實驗器材_reindexed.iloc[:,0][i], result_df_實驗器材_reindexed.iloc[:,1][i]+15, f'{result_df_實驗器材_reindexed.iloc[:, 2][i]:.2%}', fontsize=10, color='red')
# #     else:
# #         axes[0, 1].text(result_df_實驗器材_reindexed.iloc[:,0][i], result_df_實驗器材_reindexed.iloc[:,1][i]+15, f'{result_df_實驗器材_reindexed.iloc[:, 2][i]:.2%}', fontsize=10)
# # ### 添加一些图形元素
# # axes[0, 1].set_title('實驗器材滿意度', fontsize=12)
# # #axes[0, 1].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[0, 1].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[0, 1].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 教室空間 滿意度条形图
# # axes[0, 2].bar(result_df_教室空間.iloc[:,0], result_df_教室空間.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_教室空間.iloc[:,0])):
# #     axes[0, 2].text(result_df_教室空間.iloc[:,0][i], result_df_教室空間.iloc[:,1][i]+15, f'{result_df_教室空間.iloc[:, 2][i]:.2%}', fontsize=10)
# # ### 添加一些图形元素
# # axes[0, 2].set_title('教室空間滿意度', fontsize=12)
# # #axes[0, 2].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[0, 2].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[0, 2].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 教室環境 滿意度条形图
# # axes[1, 0].bar(result_df_教室環境.iloc[:,0], result_df_教室環境.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_教室環境.iloc[:,0])):
# #     axes[1, 0].text(result_df_教室環境.iloc[:,0][i], result_df_教室環境.iloc[:,1][i]+15, f'{result_df_教室環境.iloc[:, 2][i]:.2%}', fontsize=10)
# # ### 添加一些图形元素
# # axes[1, 0].set_title('教室環境滿意度', fontsize=12)
# # axes[1, 0].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[1, 0].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[1, 0].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 自學空間 滿意度条形图
# # axes[1, 1].bar(result_df_自學空間.iloc[:,0], result_df_自學空間.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_自學空間.iloc[:,0])):
# #     axes[1, 1].text(result_df_自學空間.iloc[:,0][i], result_df_自學空間.iloc[:,1][i]+15, f'{result_df_自學空間.iloc[:, 2][i]:.2%}', fontsize=10)
# # ### 添加一些图形元素
# # axes[1, 1].set_title('自學空間滿意度', fontsize=12)
# # #axes[1, 1].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[1, 1].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[1, 1].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 學校宿舍 滿意度条形图
# # axes[1, 2].bar(result_df_學校宿舍_reindexed.iloc[:,0], result_df_學校宿舍_reindexed.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_學校宿舍_reindexed.iloc[:,0])):
# #     if i==3:
# #         axes[1, 2].text(result_df_學校宿舍_reindexed.iloc[:,0][i], result_df_學校宿舍_reindexed.iloc[:,1][i]+15, f'{result_df_學校宿舍_reindexed.iloc[:, 2][i]:.2%}', fontsize=10,color='red')
# #     else:
# #         axes[1, 2].text(result_df_學校宿舍_reindexed.iloc[:,0][i], result_df_學校宿舍_reindexed.iloc[:,1][i]+15, f'{result_df_學校宿舍_reindexed.iloc[:, 2][i]:.2%}', fontsize=10)       
# # ### 添加一些图形元素
# # axes[1, 2].set_title('學校宿舍滿意度', fontsize=12)
# # #axes[1, 2].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[1, 2].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[1, 2].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 校園網路 滿意度条形图
# # axes[2, 0].bar(result_df_校園網路.iloc[:,0], result_df_校園網路.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_校園網路.iloc[:,0])):
# #     axes[2, 0].text(result_df_校園網路.iloc[:,0][i], result_df_校園網路.iloc[:,1][i]+15, f'{result_df_校園網路.iloc[:, 2][i]:.2%}', fontsize=10)
# # ### 添加一些图形元素
# # axes[2, 0].set_title('校園網路滿意度', fontsize=12)
# # #axes[2, 0].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[2, 0].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[2, 0].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 隱藏 第 8,9 張圖的軸
# # axes[2, 1].axis('off')
# # axes[2, 2].axis('off')

# # ##### 调整子图布局
# # plt.tight_layout()
# # ##### 显示整个图形
# # plt.show()
# # #%% (二二圖) 以上



# # ###### Part4-8 您最喜歡的校園地點(如無，請寫"無")
# # df_sophomore.iloc[:,37] ##  8. 您最喜歡的校園地點(如無，請寫"無")
# # ##### 将字符串按逗号分割并展平
# # split_values = df_sophomore.iloc[:,37].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # value_counts = split_values.value_counts()
# # #value_counts = df_sophomore.iloc[:,37].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二三) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('最喜歡的校園地點:')
# # print(result_df)
# # '''
# # 最喜歡的校園地點:
# #          人數     比例
# # 無      1005  0.536
# # 圖書館     409  0.218
# # 蓋夏圖書館    61  0.033
# # 體育館      32  0.017
# # 至善       22  0.012
# #     ...    ...
# # 社窩        1  0.001
# # 學餐多       1  0.001
# # no        1  0.001
# # 靜廳        1  0.001
# # 格倫樓       1  0.001

# # [187 rows x 2 columns]
# # '''
# # #### 將 index 變column
# # result_df_r = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_r.rename(columns={'index': '最喜歡的校園地點'}, inplace=True)
# # print(result_df_r)

# # '''
# #     最喜歡的校園地點    人數     比例
# # 0          無  1005  0.536
# # 1        圖書館   409  0.218
# # 2      蓋夏圖書館    61  0.033
# # 3        體育館    32  0.017
# # 4         至善    22  0.012
# # ..       ...   ...    ...
# # 182       社窩     1  0.001
# # 183      學餐多     1  0.001
# # 184       no     1  0.001
# # 185       靜廳     1  0.001
# # 186      格倫樓     1  0.001

# # [187 rows x 3 columns]
# # '''

# # result_df_r.to_excel(r'C:\Users\user\Dropbox\系務\校務研究IR\大二學生學習投入問卷調查分析\112\最喜歡的校園地點.xlsx', index=False, engine='openpyxl')
# # #%% (二三) 以上


# # ###### Part4-9 請針對校園學習環境不滿意項目提供意見或建議 (儀器設備、實驗器材、教室空間、教室環境、自學空間、學校宿舍、校園網路)(如無，請寫"無")
# # df_sophomore.iloc[:,38] ##  9. 請針對校園學習環境不滿意項目提供意見或建議 (儀器設備、實驗器材、教室空間、教室環境、自學空間、學校宿舍、校園網路)(如無，請寫"無")
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,37].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,38].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二四) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('校園學習環境不滿意項目建議:')
# # print(result_df)
# # '''
# # 校園學習環境不滿意項目建議:
# #                        人數     比例
# # 無                    1321  0.725
# # 校園網路                   13  0.007
# # 學校宿舍                    8  0.004
# # ㄨˊ                      6  0.003
# # 「無」                     5  0.003
# #                   ...    ...
# # 階梯教室的座位太擁擠、桌子太小         1  0.001
# # 宿舍網路改善，宿舍加冰箱            1  0.001
# # 校園網路還是太差                1  0.001
# # 教室內椅子不要放那麼多，校園網路很卡      1  0.001
# # 學校Wifi 思源收不到，選課介面分散     1  0.001

# # [452 rows x 2 columns]
# # '''

# # #### 將 index 變column
# # result_df_r = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_r.rename(columns={'index': '校園學習環境不滿意項目建議'}, inplace=True)
# # print(result_df_r)

# # '''
# #            校園學習環境不滿意項目建議    人數     比例
# # 0                      無  1321  0.725
# # 1                   校園網路    13  0.007
# # 2                   學校宿舍     8  0.004
# # 3                     ㄨˊ     6  0.003
# # 4                    「無」     5  0.003
# # ..                   ...   ...    ...
# # 447      階梯教室的座位太擁擠、桌子太小     1  0.001
# # 448         宿舍網路改善，宿舍加冰箱     1  0.001
# # 449             校園網路還是太差     1  0.001
# # 450   教室內椅子不要放那麼多，校園網路很卡     1  0.001
# # 451  學校Wifi 思源收不到，選課介面分散     1  0.001

# # [452 rows x 3 columns]
# # '''

# # result_df_r.to_excel(r'C:\Users\user\Dropbox\系務\校務研究IR\大二學生學習投入問卷調查分析\112\校園學習環境不滿意項目建議.xlsx', index=False, engine='openpyxl')

# # #%% (二四) 以上


# # ####### Part5  課程規劃與教師教學滿意度(依多數課程情況回答)
# # ###### Part5-1 所屬學系專業必修課程規劃
# # df_sophomore.iloc[:,40] ##  1. 所屬學系專業必修課程規劃
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,37].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,40].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二五) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('所屬學系專業必修課程規劃滿意度:')
# # print(result_df)
# # '''
# # 所屬學系專業必修課程規劃滿意度:
# #       人數     比例
# # 普通   986  0.538
# # 滿意   782  0.426
# # 不滿意   58  0.032
# # 不清楚    8  0.004
# # '''
# # #### 將 index 變column
# # result_df_專業必修 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_專業必修.rename(columns={'index': '所屬學系專業必修課程規劃滿意度'}, inplace=True)
# # print(result_df_專業必修)

# # '''
# #   所屬學系專業必修課程規劃滿意度   人數     比例
# # 0              普通  986  0.538
# # 1              滿意  782  0.426
# # 2             不滿意   58  0.032
# # 3             不清楚    8  0.004
# # '''
# # #%% (二五) 以上


# # ###### Part5-2 所屬學系專業學程規劃
# # df_sophomore.iloc[:,41] ##  2.所屬學系專業學程規劃
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,37].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,41].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二六) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('所屬學系專業學程規劃滿意度:')
# # print(result_df)
# # '''
# # 所屬學系專業學程規劃滿意度:
# #        人數     比例
# # 普通   1006  0.549
# # 滿意    763  0.416
# # 不滿意    34  0.019
# # 不清楚    31  0.017
# # '''
# # #### 將 index 變column
# # result_df_專業學程 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_專業學程.rename(columns={'index': '所屬學系專業學程規劃滿意度'}, inplace=True)
# # print(result_df_專業學程)

# # '''
# #   所屬學系專業學程規劃滿意度    人數     比例
# # 0            普通  1006  0.549
# # 1            滿意   763  0.416
# # 2           不滿意    34  0.019
# # 3           不清楚    31  0.017
# # '''
# # #%% (二六) 以上


# # ###### Part5-3 「專業必選修」課程授課老師的教學方式
# # df_sophomore.iloc[:,42] ##  3.「專業必選修」課程授課老師的教學方式
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,37].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,42].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二七) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('「專業必選修」課程授課老師的教學方式滿意度:')
# # print(result_df)
# # '''
# # 「專業必選修」課程授課老師的教學方式滿意度:
# #       人數     比例
# # 普通   998  0.544
# # 滿意   767  0.418
# # 不滿意   54  0.029
# # 不清楚   15  0.008
# # '''
# # #### 將 index 變column
# # result_df_專業必選修 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_專業必選修.rename(columns={'index': '「專業必選修」課程授課老師的教學方式滿意度'}, inplace=True)
# # print(result_df_專業必選修)

# # '''
# #   「專業必選修」課程授課老師的教學方式滿意度   人數     比例
# # 0                    普通  998  0.544
# # 1                    滿意  767  0.418
# # 2                   不滿意   54  0.029
# # 3                   不清楚   15  0.008
# # '''
# # #%% (二七) 以上



# # #%% (二七圖) 以下
# # ###### 畫圖: 課程規劃與教師教學滿意度
# # #### 設置 matplotlib 支持中文的字體: 這裡使用的是 'SimHei' 字體，您也可以替換為任何支持中文的字體
# # matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
# # matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
# # matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
# # ##### 创建一个 1x3 的子图布局
# # fig, axes = plt.subplots(1, 3, figsize=(11, 5))


# # #### 專業必修 滿意度条形图
# # axes[0].bar(result_df_專業必修.iloc[:,0], result_df_專業必修.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_專業必修.iloc[:,0])):
# #     axes[0].text(result_df_專業必修.iloc[:,0][i], result_df_專業必修.iloc[:,1][i]+15, f'{result_df_專業必修.iloc[:, 2][i]:.2%}', fontsize=14)
# # ### 添加一些图形元素
# # axes[0].set_title('專業必修滿意度', fontsize=16)
# # axes[0].set_ylabel('人數', fontsize=16)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[0].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[0].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 專業學程 滿意度条形图
# # axes[1].bar(result_df_專業學程.iloc[:,0], result_df_專業學程.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_專業學程.iloc[:,0])):
# #     axes[1].text(result_df_專業學程.iloc[:,0][i], result_df_專業學程.iloc[:,1][i]+15, f'{result_df_專業學程.iloc[:, 2][i]:.2%}', fontsize=14)
# # ### 添加一些图形元素
# # axes[1].set_title('專業學程滿意度', fontsize=16)
# # axes[1].set_ylabel('人數', fontsize=16)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[1].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[1].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 專業必選修 滿意度条形图
# # axes[2].bar(result_df_專業必選修.iloc[:,0], result_df_專業必選修.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_專業必選修.iloc[:,0])):
# #     axes[2].text(result_df_專業必選修.iloc[:,0][i], result_df_專業必選修.iloc[:,1][i]+15, f'{result_df_專業必選修.iloc[:, 2][i]:.2%}', fontsize=14)
# # ### 添加一些图形元素
# # axes[2].set_title('專業必選修滿意度', fontsize=16)
# # axes[2].set_ylabel('人數', fontsize=16)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[2].tick_params(axis='both', labelsize=12)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[2].grid(True, linestyle='--', linewidth=0.5, color='gray')

# # ##### 调整子图布局
# # plt.tight_layout()
# # ##### 显示整个图形
# # plt.show()
# # #%% (二七圖) 以上





# # ###### Part5-4 有關上述課程規劃與教師教學滿意度，針對不滿意項目提供意見或建議 (專業必修課程規劃、專業學程規劃、專業必選修課程授課老師教學方式)，如無，請填「無」。
# # df_sophomore.iloc[:,43] ##  4.有關上述課程規劃與教師教學滿意度，針對不滿意項目提供意見或建議 (專業必修課程規劃、專業學程規劃、專業必選修課程授課老師教學方式)，如無，請填「無」。
# # ##### 将字符串按逗号分割并展平
# # split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # value_counts = split_values.value_counts()
# # #value_counts = df_sophomore.iloc[:,43].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二八) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('課程規劃與教師教學建議:')
# # print(result_df)
# # '''
# # 課程規劃與教師教學建議:
# #                         人數     比例
# # 無                     1723  0.925
# # 「無」                     10  0.005
# # ㄨˊ                       4  0.002
# #                          3  0.002
# # None                     2  0.001
# #                    ...    ...
# # 林恆立不太OK                  1  0.001
# # 聽不懂                      1  0.001
# # 都亂教                      1  0.001
# # 因為16+2老師都教很快             1  0.001
# # 法原專班有太多法律系上的資訊沒有同步公布     1  0.001

# # [124 rows x 2 columns]
# # '''
# # #### 將 index 變column
# # result_df_r = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_r.rename(columns={'index': '課程規劃與教師教學建議'}, inplace=True)
# # print(result_df_r)

# # '''
# #               課程規劃與教師教學建議    人數     比例
# # 0                       無  1723  0.925
# # 1                     「無」    10  0.005
# # 2                      ㄨˊ     4  0.002
# # 3                             3  0.002
# # 4                    None     2  0.001
# # ..                    ...   ...    ...
# # 119               林恆立不太OK     1  0.001
# # 120                   聽不懂     1  0.001
# # 121                   都亂教     1  0.001
# # 122          因為16+2老師都教很快     1  0.001
# # 123  法原專班有太多法律系上的資訊沒有同步公布     1  0.001

# # [124 rows x 3 columns]
# # '''
# # result_df_r.to_excel(r'C:\Users\user\Dropbox\系務\校務研究IR\大二學生學習投入問卷調查分析\112\課程規劃與教師教學建議.xlsx', index=False, engine='openpyxl')

# # #%% (二八) 以上


# # ###### Part5-5 您覺得哪一種授課方式的學習效果比較好?
# # df_sophomore.iloc[:,44] ##  5. 您覺得哪一種授課方式的學習效果比較好?
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,44].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (二九) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('哪一種授課方式的學習效果比較好:')
# # print(result_df)
# # '''
# # 哪一種授課方式的學習效果比較好:
# #                   人數     比例
# # 實體教學             877  0.478
# # 混成教學(實體/線上課程並行)  797  0.435
# # 線上課程             157  0.086
# # 好問題                1  0.001
# # 覺得都還行              1  0.001
# # 有心上課 哪種效果都會好       1  0.001
# # '''
# # #### 將 index 變column
# # result_df_授課方式 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_授課方式.rename(columns={'index': '哪一種授課方式的學習效果比較好'}, inplace=True)
# # print(result_df_授課方式)

# # '''
# #    哪一種授課方式的學習效果比較好   人數     比例
# # 0             實體教學  877  0.478
# # 1  混成教學(實體/線上課程並行)  797  0.435
# # 2             線上課程  157  0.086
# # 3              好問題    1  0.001
# # 4            覺得都還行    1  0.001
# # 5     有心上課 哪種效果都會好    1  0.001
# # '''
# # #%% (二九) 以上

# # #%% (二九圖) 以下
# # #### 圖：哪一種授課方式的學習效果比較好
# # ### 创建图形和坐标轴
# # plt.figure(figsize=(11, 8))
# # ### 绘制条形图
# # plt.barh(result_df_授課方式.iloc[:,0], result_df_授課方式.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_授課方式.iloc[:,1])):
# #     plt.text(result_df_授課方式.iloc[:,1][i]+15, result_df_授課方式.iloc[:,0][i], f'{result_df_授課方式.iloc[:, 2][i]:.2%}', fontsize=16)

# # ### 添加一些图形元素
# # plt.title('哪一種授課方式的學習效果比較好', fontsize=16)
# # plt.xlabel('人數', fontsize=16)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # plt.tick_params(axis='both', labelsize=16)  # 同时调整x轴和y轴

# # plt.legend()
# # ### 显示网格线
# # plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
# # ### 显示图形
# # plt.show()



# # #%% (二九圖) 以上





# # ###### Part5-6 就學期間 (可複選)
# # df_sophomore.iloc[:,45] ##  6. 就學期間 (可複選)
# # ##### 将字符串按逗号分割并展平, 不拆分 '有老師能啟發您, 給您夢想跟動力'
# # #### 特定字符串
# # special_string = '有老師能啟發您, 給您夢想跟動力'
# # #### 自定义拆分函数
# # def custom_split(row):
# #     ### 如果行包含特定字符串，则先替换为占位符
# #     if special_string in row:
# #         row = row.replace(special_string, 'placeholder')
# #     ### 按照逗号、空格或顿号拆分
# #     parts = [part.strip() for part in re.split('[, ，]', row) if part.strip()]
# #     ### 将占位符替换回特定字符串
# #     return [special_string if part == 'placeholder' else part for part in parts]
# # #### 应用自定义拆分函数
# # split_values = df_sophomore['6. 就學期間 (可複選)'].apply(custom_split).explode()
# # #split_values = df_sophomore.iloc[:,45].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # value_counts = split_values.value_counts()
# # #value_counts = df_sophomore.iloc[:,45].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三十) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('在學期間遇到的老師:')
# # print(result_df)
# # '''
# # 在學期間遇到的老師:
# #                     人數     比例
# # 有碰到專心認真上課的老師      1598  0.528
# # 有老師關心您             794  0.263
# # 有老師能啟發您, 給您夢想跟動力   632  0.209
# # '''
# # #### 將 index 變column
# # result_df_遇到的老師 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_遇到的老師.rename(columns={'index': '就在學期間遇到的老師'}, inplace=True)
# # print(result_df_遇到的老師)

# # '''
# #        在學期間遇到的老師    人數     比例
# # 0      有碰到專心認真上課的老師  1598  0.528
# # 1            有老師關心您   794  0.263
# # 2  有老師能啟發您, 給您夢想跟動力   632  0.209
# # '''
# # #%% (三十) 以上


# # #%% (三十圖) 以下
# # #### 圖：在學期間遇到的老師
# # ### 创建图形和坐标轴
# # plt.figure(figsize=(11, 8))
# # ### 绘制条形图
# # plt.barh(result_df_遇到的老師.iloc[:,0], result_df_遇到的老師.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_遇到的老師.iloc[:,1])):
# #     plt.text(result_df_遇到的老師.iloc[:,1][i]+15, result_df_遇到的老師.iloc[:,0][i], f'{result_df_遇到的老師.iloc[:, 2][i]:.2%}', fontsize=16)

# # ### 添加一些图形元素
# # plt.title('在學期間遇到的老師', fontsize=16)
# # plt.xlabel('人數', fontsize=16)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # plt.tick_params(axis='both', labelsize=16)  # 同时调整x轴和y轴

# # plt.legend()
# # ### 显示网格线
# # plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
# # ### 显示图形
# # plt.show()


# # #%% (三十圖) 以上



# # ####### Part6  學生學習與輔導資源
# # ###### Part6-1 您是否申請或參與過「學生學習輔導方案」(學習輔導/自主學習/飛鷹助學) 學習輔導方案或輔導活動嗎?
# # df_sophomore.iloc[:,47] ##  1. 您是否申請或參與過「學生學習輔導方案」(學習輔導/自主學習/飛鷹助學) 學習輔導方案或輔導活動嗎?
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,47].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三一) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('您是否申請或參與過「學生學習輔導方案」(學習輔導/自主學習/飛鷹助學):')
# # print(result_df)
# # '''
# # 您是否申請或參與過「學生學習輔導方案」(學習輔導/自主學習/飛鷹助學):
# #               人數     比例
# # 否           1269  0.692
# # 是            318  0.173
# # 不知道相關方案/活動   247  0.135
# # '''
# # #### 將 index 變column
# # result_df_學習輔導 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_學習輔導.rename(columns={'index': '您是否申請或參與過「學生學習輔導方案」(學習輔導/自主學習/飛鷹助學)'}, inplace=True)
# # print(result_df_學習輔導)

# # '''
# #   您是否申請或參與過「學生學習輔導方案」(學習輔導/自主學習/飛鷹助學)    人數     比例
# # 0                                   否  1269  0.692
# # 1                                   是   318  0.173
# # 2                          不知道相關方案/活動   247  0.135
# # '''
# # #%% (三一) 以上


# # ###### Part6-2 您是否申請或參與過「生活相關輔導」(導師/領頭羊) 學習輔導方案或輔導活動嗎?
# # df_sophomore.iloc[:,48] ##  2. 您是否申請或參與過「生活相關輔導」(導師/領頭羊) 學習輔導方案或輔導活動嗎?
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,48].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三二) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('您是否申請或參與過「生活相關輔導」(導師/領頭羊):')
# # print(result_df)
# # '''
# # 您是否申請或參與過「生活相關輔導」(導師/領頭羊):
# #               人數     比例
# # 否           1145  0.624
# # 是            488  0.266
# # 不知道相關方案/活動   201  0.110
# # '''
# # #### 將 index 變column
# # result_df_生活輔導 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_生活輔導.rename(columns={'index': '您是否申請或參與過「生活相關輔導」(導師/領頭羊)'}, inplace=True)
# # print(result_df_生活輔導)

# # '''
# #   您是否申請或參與過「生活相關輔導」(導師/領頭羊)    人數     比例
# # 0                         否  1145  0.624
# # 1                         是   488  0.266
# # 2                不知道相關方案/活動   201  0.110
# # '''
# # #%% (三二) 以上


# # ###### Part6-3 您是否申請或參與過「職涯輔導」 學習輔導方案或輔導活動嗎?
# # df_sophomore.iloc[:,49] ##  3. 您是否申請或參與過「職涯輔導」 學習輔導方案或輔導活動嗎?
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,49].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三三) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('您是否申請或參與過「職涯輔導」:')
# # print(result_df)
# # '''
# # 您是否申請或參與過「職涯輔導」:
# #               人數     比例
# # 否           1297  0.707
# # 是            312  0.170
# # 不知道相關方案/活動   225  0.123
# # '''
# # #### 將 index 變column
# # result_df_職涯輔導 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_職涯輔導.rename(columns={'index': '您是否申請或參與過「職涯輔導」'}, inplace=True)
# # print(result_df_職涯輔導)

# # '''
# #   您是否申請或參與過「職涯輔導」    人數     比例
# # 0               否  1297  0.707
# # 1               是   312  0.170
# # 2      不知道相關方案/活動   225  0.123
# # '''
# # #%% (三三) 以上



# # ###### Part6-4 您是否申請或參與過「外語教學中心學習輔導」 學習輔導方案或輔導活動嗎?
# # df_sophomore.iloc[:,50] ##  4. 您是否申請或參與過「外語教學中心學習輔導」 學習輔導方案或輔導活動嗎?
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,50].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三四) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('您是否申請或參與過「外語教學中心學習輔導」:')
# # print(result_df)
# # '''
# # 您是否申請或參與過「外語教學中心學習輔導」:
# #               人數     比例
# # 否           1170  0.638
# # 是            453  0.247
# # 不知道相關方案/活動   211  0.115
# # '''
# # #### 將 index 變column
# # result_df_外語教學中心學習輔導 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_外語教學中心學習輔導.rename(columns={'index': '您是否申請或參與過「外語教學中心學習輔導」'}, inplace=True)
# # print(result_df_外語教學中心學習輔導)

# # '''
# #   您是否申請或參與過「外語教學中心學習輔導」    人數     比例
# # 0                     否  1170  0.638
# # 1                     是   453  0.247
# # 2            不知道相關方案/活動   211  0.115
# # '''
# # #%% (三四) 以上


# # ###### Part6-5 您是否申請或參與過「諮商暨健康中心的諮商輔導」 學習輔導方案或輔導活動嗎?
# # df_sophomore.iloc[:,51] ##  5. 您是否申請或參與過「諮商暨健康中心的諮商輔導」 學習輔導方案或輔導活動嗎?
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,51].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三五) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('您是否申請或參與過「諮商暨健康中心的諮商輔導」:')
# # print(result_df)
# # '''
# # 您是否申請或參與過「諮商暨健康中心的諮商輔導」:
# #               人數     比例
# # 否           1351  0.737
# # 是            254  0.138
# # 不知道相關方案/活動   229  0.125
# # '''
# # #### 將 index 變column
# # result_df_諮商暨健康中心諮商輔導 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_諮商暨健康中心諮商輔導.rename(columns={'index': '您是否申請或參與過「諮商暨健康中心的諮商輔導」'}, inplace=True)
# # print(result_df_諮商暨健康中心諮商輔導)

# # '''
# #   您是否申請或參與過「諮商暨健康中心的諮商輔導」    人數     比例
# # 0                       否  1351  0.737
# # 1                       是   254  0.138
# # 2              不知道相關方案/活動   229  0.125
# # '''
# # #%% (三五) 以上


# # ###### Part6-6 您是否申請或參與過「國際化資源」 學習輔導方案或輔導活動嗎?
# # df_sophomore.iloc[:,52] ##  6. 您是否申請或參與過「國際化資源」 學習輔導方案或輔導活動嗎?
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,43].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,52].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三六) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('您是否申請或參與過「國際化資源」 學習輔導方案或輔導活動:')
# # print(result_df)
# # # '''
# # # 您是否申請或參與過「國際化資源」 學習輔導方案或輔導活動:
# # #               人數     比例
# # # 否           1289  0.703
# # # 不知道相關方案/活動   273  0.149
# # # 是            272  0.148
# # # '''
# # #### 將 index 變column
# # result_df_國際化資源 = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_國際化資源.rename(columns={'index': '您是否申請或參與過「國際化資源」 學習輔導方案或輔導活動'}, inplace=True)
# # print(result_df_國際化資源)
# # # '''
# # #   您是否申請或參與過「國際化資源」 學習輔導方案或輔導活動    人數     比例
# # # 0                            否  1289  0.703
# # # 1                   不知道相關方案/活動   273  0.149
# # # 2                            是   272  0.148
# # # '''
# # #### 對調 '不知道相關方案/活動' 與 '是' 的index 次序, 因為要與其他圖的項目順序一致
# # result_df_國際化資源_reindexed = result_df_國際化資源.reindex([0,2,1])
# # result_df_國際化資源_reindexed = result_df_國際化資源_reindexed.reset_index(drop=True)  ## 重設 index
# # print(result_df_國際化資源_reindexed)
# # '''
# #   您是否申請或參與過「國際化資源」 學習輔導方案或輔導活動    人數     比例
# # 0                            否  1289  0.703
# # 2                            是   272  0.148
# # 1                   不知道相關方案/活動   273  0.149
# # '''
# # #%% (三六) 以上


# # #%% (三六圖) 以下
# # ###### 畫圖: 申請或參與過之學習輔導方案或輔導活動
# # ##### 创建一个 2x3 的子图布局
# # fig, axes = plt.subplots(2, 3, figsize=(11, 8))

# # #### 申請或參與過學生學習輔導方案 条形图
# # axes[0,0].bar(result_df_學習輔導.iloc[:,0], result_df_學習輔導.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_學習輔導.iloc[:,0])):
# #     axes[0,0].text(result_df_學習輔導.iloc[:,0][i], result_df_學習輔導.iloc[:,1][i]+15, f'{result_df_學習輔導.iloc[:, 2][i]:.2%}', fontsize=12)
# # ### 添加一些图形元素
# # axes[0, 0].set_title('申請或參與過學生學習輔導方案', fontsize=12)
# # axes[0, 0].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[0, 0].tick_params(axis='both', labelsize=10)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[0, 0].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 申請或參與過生活相關輔導 条形图
# # axes[0, 1].bar(result_df_生活輔導.iloc[:,0], result_df_生活輔導.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_生活輔導.iloc[:,0])):
# #     axes[0, 1].text(result_df_生活輔導.iloc[:,0][i], result_df_生活輔導.iloc[:,1][i]+15, f'{result_df_生活輔導.iloc[:, 2][i]:.2%}', fontsize=12)
# # ### 添加一些图形元素
# # axes[0, 1].set_title('申請或參與過生活相關輔導', fontsize=12)
# # axes[0, 1].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[0, 1].tick_params(axis='both', labelsize=10)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[0, 1].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 申請或參與過職涯輔導 条形图
# # axes[0, 2].bar(result_df_職涯輔導.iloc[:,0], result_df_職涯輔導.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_職涯輔導.iloc[:,0])):
# #     axes[0, 2].text(result_df_職涯輔導.iloc[:,0][i], result_df_職涯輔導.iloc[:,1][i]+15, f'{result_df_職涯輔導.iloc[:, 2][i]:.2%}', fontsize=12)
# # ### 添加一些图形元素
# # axes[0, 2].set_title('申請或參與過職涯輔導', fontsize=12)
# # axes[0, 2].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[0, 2].tick_params(axis='both', labelsize=10)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[0, 2].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 申請或參與過外語教學中心學習輔導 条形图
# # axes[1, 0].bar(result_df_外語教學中心學習輔導.iloc[:,0], result_df_外語教學中心學習輔導.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_外語教學中心學習輔導.iloc[:,0])):
# #     axes[1, 0].text(result_df_外語教學中心學習輔導.iloc[:,0][i], result_df_外語教學中心學習輔導.iloc[:,1][i]+15, f'{result_df_外語教學中心學習輔導.iloc[:, 2][i]:.2%}', fontsize=12)
# # ### 添加一些图形元素
# # axes[1, 0].set_title('申請或參與過外語教學中心學習輔導', fontsize=12)
# # axes[1, 0].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[1, 0].tick_params(axis='both', labelsize=10)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[1, 0].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 申請或參與過諮商暨健康中心的諮商輔導 条形图
# # axes[1, 1].bar(result_df_諮商暨健康中心諮商輔導.iloc[:,0], result_df_諮商暨健康中心諮商輔導.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_諮商暨健康中心諮商輔導.iloc[:,0])):
# #     axes[1, 1].text(result_df_諮商暨健康中心諮商輔導.iloc[:,0][i], result_df_諮商暨健康中心諮商輔導.iloc[:,1][i]+15, f'{result_df_諮商暨健康中心諮商輔導.iloc[:, 2][i]:.2%}', fontsize=12)
# # ### 添加一些图形元素
# # axes[1, 1].set_title('申請或參與過諮商暨健康中心的諮商輔導', fontsize=12)
# # axes[1, 1].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[1, 1].tick_params(axis='both', labelsize=10)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[1, 1].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # #### 申請或參與過國際化資源 条形图
# # axes[1, 2].bar(result_df_國際化資源_reindexed.iloc[:,0], result_df_國際化資源_reindexed.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_國際化資源_reindexed.iloc[:,0])):
# #     if i==2:
# #         axes[1, 2].text(result_df_國際化資源_reindexed.iloc[:,0][i], result_df_國際化資源_reindexed.iloc[:,1][i]+15, f'{result_df_國際化資源_reindexed.iloc[:, 2][i]:.2%}', fontsize=12, color='red')
# #     else:
# #         axes[1, 2].text(result_df_國際化資源_reindexed.iloc[:,0][i], result_df_國際化資源_reindexed.iloc[:,1][i]+15, f'{result_df_國際化資源_reindexed.iloc[:, 2][i]:.2%}', fontsize=12)
# # ### 添加一些图形元素
# # axes[1, 2].set_title('申請或參與過國際化資源', fontsize=12)
# # axes[1, 2].set_ylabel('人數', fontsize=12)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # axes[1, 2].tick_params(axis='both', labelsize=10)  # 同时调整x轴和y轴
# # #axes[0, 1].legend()
# # ### 显示网格线
# # axes[1, 2].grid(True, linestyle='--', linewidth=0.5, color='gray')


# # ##### 调整子图布局
# # plt.tight_layout()
# # ##### 显示整个图形
# # plt.show()
# # #%% (三六圖) 以上



# # ###### Part6-7 那些學習輔導方案或輔導活動對您是有幫助的?
# # df_sophomore.iloc[:,53] ##  7. 那些學習輔導方案或輔導活動對您是有幫助的?
# # ##### 将字符串按逗号分割并展平
# # split_values = df_sophomore.iloc[:,53].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # value_counts = split_values.value_counts()
# # #value_counts = df_sophomore.iloc[:,52].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三七) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('那些學習輔導方案或輔導活動對您是有幫助的:')
# # print(result_df)
# # '''
# # 那些學習輔導方案或輔導活動對您是有幫助的:
# #                            人數     比例
# # 生活相關輔導(導師/領頭羊)            755  0.237
# # 學生學習輔導方案(學習輔導/自主學習/飛鷹助學)  628  0.198
# # 職涯輔導                      561  0.176
# # 國際化資源                     507  0.159
# # 外語教學中心學習輔導                491  0.154
# # 諮商暨健康中心的諮商輔導              237  0.075
# # '''
# # #### 將 index 變column
# # result_df_r = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_r.rename(columns={'index': '那些學習輔導方案或輔導活動對您是有幫助的'}, inplace=True)
# # print(result_df_r)

# # '''
# #         那些學習輔導方案或輔導活動對您是有幫助的   人數     比例
# #  0            生活相關輔導(導師/領頭羊)  755  0.237
# #  1  學生學習輔導方案(學習輔導/自主學習/飛鷹助學)  628  0.198
# #  2                      職涯輔導  561  0.176
# #  3                     國際化資源  507  0.159
# #  4                外語教學中心學習輔導  491  0.154
# #  5              諮商暨健康中心的諮商輔導  237  0.075
# # '''
# # #%% (三七) 以上


# # #%% (三七圖) 以下
# # #### 圖：哪些學習輔導方案或輔導活動對學生有幫助
# # ### 创建图形和坐标轴
# # plt.figure(figsize=(11, 8))
# # ### 绘制条形图
# # plt.bar(result_df_r.iloc[:,0], result_df_r.iloc[:,1])
# # #plt.barh(series.index, series)
# # ### 標示數據
# # for i in range(len(result_df_r.iloc[:,0])):
# #     plt.text(result_df_r.iloc[:,0][i], result_df_r.iloc[:,1][i]+15, f'{result_df_r.iloc[:, 2][i]:.2%}', fontsize=16)

# # ### 添加一些图形元素
# # plt.title('哪些學習輔導方案或輔導活動對學生有幫助', fontsize=16)
# # plt.ylabel('人數', fontsize=16)
# # #plt.ylabel('本校現在所提供的資源或支援事項')
# # ### 调整x轴和y轴刻度标签的字体大小
# # plt.tick_params(axis='both', labelsize=16)  # 同时调整x轴和y轴

# # plt.legend()
# # ### 显示网格线
# # plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
# # ### 显示图形
# # plt.show()



# # #%% (三七圖) 以上



# # ###### Part6-8 您在課業上，是否有其他需要協助的，如無，請填「無」。
# # df_sophomore.iloc[:,54] ##  8. 您在課業上，是否有其他需要協助的，如無，請填「無」。
# # ##### 将字符串按逗号分割并展平
# # #split_values = df_sophomore.iloc[:,54].str.split(',| |，|、').explode()
# # # ##### 过滤出只包含'是'或'否'的子字符串
# # # filtered_values = split_values[split_values.isin(['是', '否'])]
# # ##### 计算不同子字符串的出现次数
# # #value_counts = split_values.value_counts()
# # value_counts = df_sophomore.iloc[:,54].value_counts()
# # ##### 计算不同子字符串的比例
# # proportions = value_counts / value_counts.sum()

# # #%% (三八) 以下
# # ##### 创建一个新的DataFrame来显示结果
# # result_df = pd.DataFrame({
# #     '人數': value_counts,
# #     '比例': proportions.round(3)
# # })
# # print('您在課業上，是否有其他需要協助的:')
# # print(result_df)
# # '''
# # 您在課業上，是否有其他需要協助的:
# #                         人數     比例
# # 無                     1737  0.952
# # 「無」                      9  0.005
# # 有                        3  0.002
# # 無，                       2  0.001
# # None                     2  0.001
# #                    ...    ...
# # 想要學校多舉辦職涯分享式的演講          1  0.001
# # 上課集中力不足，很常想睡             1  0.001
# # 想找學習夥伴，但我不太有時間去參與學習      1  0.001
# # 老師和我相讨一下讀寫障礙專注力不足的調整     1  0.001
# # 轉學生需要輔導直屬                1  0.001

# # [76 rows x 2 columns]
# # '''
# # #### 將 index 變column
# # result_df_r = result_df.reset_index()
# # #### 重新命名新的column
# # result_df_r.rename(columns={'index': '您在課業上，是否有其他需要協助的'}, inplace=True)
# # print(result_df_r)

# # '''
# #          您在課業上，是否有其他需要協助的    人數     比例
# #  0                      無  1737  0.952
# #  1                    「無」     9  0.005
# #  2                      有     3  0.002
# #  3                     無，     2  0.001
# #  4                   None     2  0.001
# #  ..                   ...   ...    ...
# #  71       想要學校多舉辦職涯分享式的演講     1  0.001
# #  72          上課集中力不足，很常想睡     1  0.001
# #  73   想找學習夥伴，但我不太有時間去參與學習     1  0.001
# #  74  老師和我相讨一下讀寫障礙專注力不足的調整     1  0.001
# #  75             轉學生需要輔導直屬     1  0.001

# #  [76 rows x 3 columns]
# # '''
# # result_df_r.to_excel(r'C:\Users\user\Dropbox\系務\校務研究IR\大二學生學習投入問卷調查分析\112\您在課業上是否有其他需要協助的.xlsx', index=False, engine='openpyxl')
# # #%% (三八) 以上















