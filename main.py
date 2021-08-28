# -*- coding:utf-8 -*-
# noinspection PyBroadException
"""
作者：luoyulong
日期：2021年08月
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys


def now():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


class GoodDoctorEducation(object):
    """
    好医生继续教育自动化学习
    """

    def __init__(self, user_ame="123", passwd="123"):
        self.current_video_elem = None
        self.passed_item = []
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome()
        self.main_url = 'http://www.cmechina.net/index.jsp'
        self.current_time = ""
        self.user_name = user_ame
        self.passwd = passwd
        self.questions_dic = {}

    def log_in(self):
        """
        登陆函数
        :return:
        """
        self.browser.get(url=self.main_url)
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="login_name"]').send_keys(self.user_name)
        time.sleep(0.05)
        self.browser.find_element_by_xpath('//*[@id="login_pass"]').send_keys(self.passwd)
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="login_but"]').click()
        print('log in success！')
        time.sleep(2)
        try:
            self.browser.find_element_by_xpath('/html/body/div/div[2]/a').click()
        except Exception:
            pass
        time.sleep(1)
        self.select_class()

    def select_class(self):
        """
        选课界面，默认学习完当前页面;
        :return:
        """
        self.browser.get('http://www.cmechina.net/cme/subject.jsp?subjectId=02-01')
        time.sleep(2)
        class_to_learn_xpath = '//*[@id="indexTabs"]/div[1]/ul/li/p[1]/a'
        class_to_learn_elem = self.browser.find_elements_by_xpath(class_to_learn_xpath)
        for each_class in class_to_learn_elem:
            class_name = each_class.text
            class_url = each_class.get_attribute('href')
            print(f"ready to study-->{class_name}")
            self.passed_item.append(class_name)
            new_window = 'window.open("{}")'.format(class_url)
            self.browser.execute_script(new_window)
            self.browser.switch_to.window(self.browser.window_handles[-1])
            self.get_lesson()
            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[-1])
            print(f"subject complete-->{class_name}")
            print("=" * 70)
        for i in self.passed_item:
            print("subject complete-->", i)
        print("=" * 70)
        input("all subject have been completed,exiting. . .")

    def get_lesson(self):
        """
        进入所选课程页面;从页面获取每一个小课学习状态，并判断进入学习
        :return:
        """
        click = False
        for_study_title = ""
        lesson_name_and_url = self.browser.find_elements_by_xpath('//*[@id="course_list"]/h3/a')
        statues = self.browser.find_elements_by_xpath('//*[@id="course_list"]/div/a/span')
        for index, lesson in enumerate(lesson_name_and_url):
            print(lesson.text, "-->", statues[index].text)
            if statues[index].text != "考试通过":
                for_study_title = lesson.text
                print("-->start")
                click = True
                lesson.click()
                break
        if click:
            self.video_cycle(for_study_title)
        else:
            return

    def video_cycle(self, lesson_title):
        """
        进入视频播放;
        通过js函数设置播放、播放速度、检测播放时间、是否完成；
        :param lesson_title: 当前所学课程名称
        :return:
        """
        time.sleep(3)
        self.browser.execute_script('return document.readyState')
        while True:
            if self.browser.execute_script('return document.readyState') == "complete":
                break
            self.browser.refresh()
            time.sleep(3)
        while True:
            try:
                self.browser.execute_script('document.querySelector("video").play()')
                break
            except:
                self.browser.refresh()
            time.sleep(1)
        self.browser.execute_script('document.querySelector("video").volume=0.0')
        lessons_name_and_url = self.browser.find_elements_by_xpath('//*[@id="s_r_ml"]/li/a')
        lessons_index = self.browser.find_elements_by_xpath('//*[@id="s_r_ml"]/li/a/span')
        lessons_statue = self.browser.find_elements_by_xpath('//*[@id="s_r_ml"]/li/i')
        lessons_list = []
        for index, lesson in enumerate(lessons_name_and_url):
            lesson_index = lessons_index[index].text
            lesson_name = lesson.text
            lesson_statue = lessons_statue[index].text
            lessons_list.append((lesson, lesson_index, lesson_name, lesson_statue))
        time.sleep(1)
        speed = 2
        same_count = 0
        while True:
            if speed < 12:
                speed += 2
            else:
                speed -= 4
            self.browser.execute_script(f'document.querySelector("video").playbackRate={speed}')
            is_end = self.browser.execute_script('return document.querySelector("video").ended')
            if is_end:
                print("video ended,go to exam")
                break
            else:
                current_time = self.browser.execute_script('return document.querySelector("video").currentTime')
                duration_time = self.browser.execute_script('return document.querySelector("video").duration')
                try:
                    progress = float(current_time) / float(duration_time)
                except:
                    progress = 1.0
                progress = round(progress * 100, 2)
                if self.current_time == current_time:
                    if "单选题" in self.browser.page_source:
                        self.exam_in_video()
                    same_count += 1
                    if same_count >= 10:
                        print("the video may cause something wrong,try exit.")
                        break
                else:
                    self.current_time = current_time
                sys.stdout.flush()
                sys.stdout.write(
                    f"{lesson_title}-->|"
                    f"progress:{progress}%"
                    f"|currentTime:{round(current_time, 2)}"
                    f"|totalTime:{round(duration_time, 2)}"
                    f"|speed:{speed}")
                time.sleep(2)
                sys.stdout.write("\r")
        self.exam()

    def exam_in_video(self):
        """
        部分课程中设置有随机测试题;
        :return:
        """
        answer_lst = self.browser.find_elements_by_xpath('//*[@id="t_list"]/li/label/input')
        for answer in answer_lst:
            try:
                answer.click()
                self.browser.find_element_by_xpath("//input[@value='提交答案']").click()
                time.sleep(1)
            except:
                pass
            try:
                self.browser.find_element_by_xpath("//input[@value='继续学习']").click()
            except:
                pass

    def exam(self):
        """
        通过js调用gotoExam（）函数，进入考试
        :return:
        """
        try:
            self.browser.execute_script('gotoExam()')
        except:
            self.video_cycle("Repetitive learning！")
        time.sleep(1)
        question_titles = self.browser.find_elements_by_xpath('/html/body/div[2]/div/div/div/form/ul/li/h3')
        self.questions_dic = {}
        for question in question_titles:
            answer_lst = []
            question_title = question.text[2:]
            question_xpath = f"//h3[contains(text(),'{question_title}')]"
            answers_xpath_new = question_xpath + "/../p"
            answers_elem = self.browser.find_elements_by_xpath(answers_xpath_new)
            for index, each in enumerate(answers_elem):
                answer_lst.append(each.text)
            self.questions_dic[question_title] = answer_lst
        for each in self.questions_dic:
            # TODO 这里需要调整，当一个网页中，有两个相同的答案
            option_string = f"//p[contains(.,'{self.questions_dic[each][0]}')]/input"
            option_elem = self.browser.find_elements_by_xpath(option_string)
            for option in option_elem:
                option_name = option.get_attribute('name')
                father_title = self.browser.find_element_by_xpath(f'//*[@name="{option_name}"]/../../h3').text
                if each in father_title:
                    option.click()
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="tjkj"]').click()
        time.sleep(1)
        self.result_judgement()

    def result_judgement(self):
        """
        判断提交考试后的页面
        :return:
        """
        page_source = self.browser.page_source
        if "继续学习下一节" in page_source:
            print("exam passed,try the next lesson")
            self.browser.find_element_by_xpath('/html/body/div[4]/div/div[1]/a').click()
            time.sleep(2)
            self.get_lesson()
        elif "申请学分" in self.browser.page_source:
            return
        else:
            print("exam failed,try it again!")
            result_elem = self.browser.find_elements_by_xpath('/html/body/div[2]/div/div/div/div[2]/div[2]/p')
            for i in result_elem:
                result = i.text
                for k in self.questions_dic:
                    if k in result:
                        print(f"Question[{k}] contains a wrong answer,try to remove it.")
                        old_lst = self.questions_dic[k]
                        self.questions_dic[k] = old_lst[1:]
            self.browser.find_element_by_xpath('//a[contains(text(),"重新答题")]').click()
            time.sleep(1)
            self.re_exam()

    def re_exam(self):
        """
        考试未通过时，循环调用此函数
        :return:
        """
        for each in self.questions_dic:
            option_string = f"//p[contains(.,'{self.questions_dic[each][0]}')]/input"
            option_elem = self.browser.find_elements_by_xpath(option_string)
            for option in option_elem:
                option_name = option.get_attribute('name')
                father_title = self.browser.find_element_by_xpath(f'//*[@name="{option_name}"]/../../h3').text
                if each in father_title:
                    option.click()
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="tjkj"]').click()
        time.sleep(1)
        self.result_judgement()


if __name__ == '__main__':
    userName = input("userName:")
    passWord = input("passWord:")
    # py = 'emilypyh314','pyh19890804'
    # wxl = '18375910742','wangxl19911021'
    current_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    app = GoodDoctorEducation(userName, passWord)
    app.log_in()
