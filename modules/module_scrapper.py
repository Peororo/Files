from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd


infos = []
collated_timetable = pd.DataFrame()

driver = webdriver.Chrome()
driver.get('https://wish.wis.ntu.edu.sg/webexe/owa/aus_schedule.main')

optElem = driver.find_elements_by_tag_name('option')
courses = optElem[21:] # change this, involves sem form 1st option

for i, course in enumerate(courses):

    # remove headers that leads to nothing
    if course.text == ' ' or '---' in course.text:
        pass

    else:

        # select module and click load
        course_name = course.text
        
        # click on one of the course
        driver.find_element_by_xpath(f'//*[@id="ui_body_container"]/table/tbody/tr/td[2]/select[2]/option[{i+1}]').click() 
        
        # click load class schedule
        driver.find_element_by_xpath('//*[@id="ui_body_container"]/table/tbody/tr/td[2]/input').click()
        
        # switch to 2nd window
        driver.switch_to.window(driver.window_handles[1])
        
        # get course name
        course_name = driver.find_element_by_xpath('/html/body/center/center/font[1]/b/b/font').text.split('\n')[1]
        print(f'\nScanning: {course_name}')
        
        # scrape module details
        for no, module in enumerate(driver.find_elements_by_tag_name('table')):
            
            # retrieve info column
            if no % 2 == 0:

                info = []
                df = pd.read_html(driver.find_elements_by_tag_name('table')[no].get_attribute('outerHTML'))[0]
                                                
                # get column details
                info = list(df.iloc[0])
                
                # add flag for PT
                mod_code = f'{info[0]} {"PT" if "PartTime" in course_name else ""}'
                mod_name = f'{info[1]} {"PT" if "PartTime" in course_name else ""}'
                
                info[0] = mod_code
                info[1] = mod_name
                print(f'\t{mod_code}: {mod_name}')

                # check for prereq (row)
                try:
                    info.append(' '.join(df[1].iloc[1:]))
                except TypeError:
                    pass

                infos.append(info)
            
            # retrieve timetable
            elif no % 2 == 1:
                
                timetable = pd.read_html(driver.find_elements_by_tag_name('table')[no].get_attribute('outerHTML'))[0]
                
                # replace 1st column as headers, NOTE: throws FutureWarning
                # timetable.columns = timetable.iloc[0]
                # timetable.drop([0], axis = 0, inplace = True)

                # fill all na in INDEX and REMARK
                timetable.fillna(method='ffill', inplace = True)

                # drop all lectures since duplicates
                timetable.drop_duplicates(subset = ['TYPE','GROUP','DAY','TIME','VENUE'], inplace = True)
                
                # set new column as module code
                timetable['MODULE'] = mod_code
                timetable['NAME'] = mod_name
                
                # change index number of LEC, ignore if empty e.g. online courses
                try:
                    timetable.loc[timetable.TYPE == 'LEC/STUDIO', 'INDEX'] = 'LEC'
                except TypeError:
                    pass
                
                collated_timetable = collated_timetable.append(timetable)
                
        # close and switch back to first window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
driver.close()

# save timetable
collated_timetable.drop_duplicates(inplace = True)
collated_timetable.to_csv('timetable.csv')

# save module infomation
infos_df = pd.DataFrame(infos, columns = ['CODE', 'TITLE', 'AU', 'PREREQUISITE'])
infos_df.drop_duplicates(inplace = True)
infos_df.to_csv('modules_info1.csv')