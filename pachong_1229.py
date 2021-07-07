from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import urllib.parse
# 保持会话
# 新建一个session对象
sess = requests.session()
 
afterLogin_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0','cookie':'QCCSESSID=你的session'}

# sess.post('https://www.qcc.com',data=login,header s=afterLogin_headers)

data_result = 'filter={"i":["C","E"],"r":[{"pr":"JS"},{"pr":"SH"}],'\
    '"d":[{"start":"20180113","end":"20200113"}],"ct":["10"],"f":["T","N_S"],"t":[]}'\
    '&viewResult=true&'\
    'filterTexts=[{"name":"行业分类：制造业,建筑业","field":"industry"},'\
    '{"name":"省份地区：江苏省,上海市","field":"country"},'\
    '{"name":"成立日期：1-3年","field":"startDate"},'\
    '{"name":"企业类型：有限责任公司","field":"coyType"},'\
    '{"name":"有联系电话","field":"advance","key":"tel"},'\
    '{"name":"无失信信息","field":"advance","key":"shixin"}]' 

datas = urllib.parse.quote(data_result)

def get_company_message(company):
    list_company = []
    phone_information = []
    email_information = []
    website_information = []
    address_information = []
    fx_none  = []
    fx_pc = []
    ressss = [] 

    #获取查询到的网页内容（全部）
    details = sess.get(company,headers=afterLogin_headers,timeout=10)
    details.raise_for_status()
    details.encoding = 'utf-8' 
    details_soup = BeautifulSoup(details.text,features="html.parser")
    messages = details_soup.text
    time.sleep(5)
    if '关联风险' in messages:
        # print('存在风险',company)
        #企业名
        h1_title = details_soup.select('h1')
        h1_value = h1_title[0].string
        # print('存在风险企业民为:{0}'.format(h1_value))
        #电话
        phone = details_soup.find("span",style="color: #000;")
        phone_result = phone.text
        # print(phone_result)
        # #官网
        website = details_soup.find_all("span",class_='cvlu')
        website_result = website[1].text.strip()
        # print(website_result)
        # #邮箱
        email = details_soup.find_all("span",class_='cvlu')
        email_result = email[2].text.strip()
        # print(email_result)
        # #地址
        address = details_soup.find_all("span",class_='cvlu')
        address_result = address[3].text.strip()
        # print(address_result)
        
        # unique值
        result_value = re.findall(r'(\w*).html',company)[0]
        # print(result_value)
    
        # companyname值为h1_value
        # 诉讼url
        list_company.append(h1_value)
        phone_information.append(phone_result)
        website_information.append(website_result)
        email_information.append(email_result)
        address_information.append(address_result)
        
        susong_url = 'https://www.qcc.com/company_getinfos?unique=' + str(result_value) + '&companyname=' + str(h1_value) + '&tab=susong'
        # print(susong_url)
        susong_result = sess.get(susong_url,headers=afterLogin_headers).text
        try:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
            if '申请人' in susong_result:
                # sonp = BeautifulSoup(susong_result,features="lxml")
                # sonp_result = sonp.find_all("a",class_="c_a")
                fx_none.append('存在法律诉讼')
                fx_pc.append('存在风险')
                try:
                    result = re.compile(r'<td width="\d{1,2}%">(.*?)</td>', re.DOTALL)
                    result_re = result.findall(susong_result)


                    #法律详情
                    for x in result_re:
                        x2 = x.replace("\n", "").replace(" ", "").replace("<br/>", "").replace("</a>", "").replace("\t", "").replace("<br>", "")
                        # print(x2)
                        if '上诉人' in x2 or '原告' in x2 or '被上诉人' in x2 or '申请执行人' in x2 or '被执行人' in x2: 
                            pre = re.compile('[\u4e00-\u9fa5]+[\/\-\,]?[\u4e00-\u9fa5]+')
                            text= ''.join(pre.findall(x2))
                            ressss.append(text)
                        else:
                            pass
                        
                except ValueError:
                    print('该链接查询失败{0}'.format(susong_url))
            else:
                # print('不存在法律责任')
                ressss.append('不存在法律责任')
                fx_none.append('不存在法律诉讼')
                fx_pc.append('不存在风险')
        except :
            pass
    else:
        list_company = ['空']
        phone_information = ['空']
        email_information = ['空']
        website_information = ['空']
        address_information = ['空']
        ressss = ['空']
        fx_none  = ['空']
        fx_pc = ['空']

    # 筛选重复值
    ressss_value = sorted(set(ressss), key=ressss.index)

    df = pd.DataFrame({'公司':list_company,\
                        '电话':phone_information,\
                        '邮箱':email_information,\
                        '官网网址':website_information,\
                        '公司地址':address_information,\
                        '是否存在诉讼':fx_none,\
                        '法律详情':[ressss_value],\
                        '是否存在风险':fx_pc
    })
    return df
    
    

num = 0

for n in range(1,2):
    vars_vale = sess.get('https://www.qcc.com/',headers=afterLogin_headers)
    search = sess.post('https://www.qcc.com/search_adsearchmultilist?p={0}'.format(n),data=datas,headers=afterLogin_headers)
    search.raise_for_status()
    # print(vars_vale.text)
    # print(search.text)
    search.encoding = 'utf-8' 
    soup = BeautifulSoup(search.text,features="html.parser")
    href = soup.find_all('a',href=True)
    href = soup.find_all('a',{'class': 'ma_h1'})
    time.sleep(5)
    
    for a in href:
        b = a['href']
        pt_url = 'https://www.qcc.com' + str(b)
        # print(pt_url)
        try:
            messages = get_company_message(pt_url)
            if num == 0:
                messages.to_csv('/Users/bw/Desktop/cc.csv',index=False,header=True)
            else:
                messages.to_csv('/Users/bw/Desktop/cc.csv',mode='a+',index=False,header=False)
        except :
            pass
        num += 1
        time.sleep(4)

