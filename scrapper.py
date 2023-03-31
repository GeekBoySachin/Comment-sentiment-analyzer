from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from logger import logging
import selectors_repository
import os,sys
from config import MONGO_URI
from exception import ScrapperException
from mongodboperations import MongoOperations


class Scrapper:
    def __init__(self, youtube_video_link):
        """Initilize Scrapper class

        Args:
            youtuber_video_link (str)): Youtube video link
        """
        self.selector_store = selectors_repository.Selectors()
        self.logger = logging.getLogger()
        self.chrome_driver_download_path = os.getcwd()+"\\drivers"
        self.options = self.get_chrome_options()
        self.driver_path = ChromeDriverManager(path=self.chrome_driver_download_path).install()
        self.driver = None
        self.youtube_video_link = youtube_video_link

    def get_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("disable-dev-shm-usage")
        options.add_argument("--window-size=1366,768")
        options.add_argument("--headless")
        return options

    def open_video_link(self, video_link):
        """
        :param video_link: str
        :return: Boolean
        """
        try:
            self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
            self.driver.get(video_link)
        except Exception as e:
            raise ScrapperException(e,sys)

    def get_website_element(self, selector_type, selector):
        """
        :param selector_type: str
        :param selector: str
        :return: web element
        """
        try:
            element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((selector_type, selector)))
            return element
        except Exception as e:
            raise ScrapperException(e,sys)

    def get_many_website_elements(self, selector_type, selector):
        """
        :param selector_type:str
        :param selector:str
        :return: list(web element)
        """
        try:
            elements = WebDriverWait(self.driver, 60).until(EC.presence_of_all_elements_located((selector_type,
                                                                                                selector)))
            return elements
        except Exception as e:  
            raise ScrapperException(e, sys)

    def get_value_from_element(self, element, value_type):
        """
        :param element: web element
        :param value_type: str
        :return: str
        """
        try:
            result = element.get_property(value_type)
            result = self.filter_textcontent(result)
            return result
        except Exception as e:
            raise ScrapperException(e,sys)

    def scroll_video_page(self, times):
        """
        :param times: int
        :return: None
        """
        self.logger.info("Scrolling page to load video elements in DOM")
        i = 0
        while i < times:
            length = self.driver.execute_script("return window.scrollY")
            self.driver.execute_script("window.scrollTo(arguments[0],arguments[0]+200);", length)
            time.sleep(1)
            i += 1
        self.logger.info("Scrolling complete")

    def find_youtuber_name(self):
        """
        :return: str | None
        """
        element = self.get_website_element(By.CSS_SELECTOR, self.selector_store.get_youtuber_name_css())
        if element is not None:
            youtube_name = self.get_value_from_element(element, "textContent")
            if youtube_name is not None:
                return youtube_name.strip()


    def get_title_of_video(self):
        """
        :param element: web element
        :return: str | None
        """
        title_element = self.get_website_element(By.CSS_SELECTOR,self.selector_store.get_video_title_css2())
        if title_element is not None:
            title = self.get_value_from_element(title_element, "textContent")
            if title is not None:
                return title
            else:
                return "not found"

    def find_no_of_comments(self):
        """
        :return: str | None
        """
        comment_section_element = self.get_website_element(By.CSS_SELECTOR,
                                                           self.selector_store.get_video_comment_section_css())
        if comment_section_element is not None:
            self.logger.info(f"Comment section loaded :{comment_section_element}")
            no_of_comments_element = self.get_website_element(By.XPATH, self.selector_store.get_video_no_comments_xpath())
            if no_of_comments_element is not None:
                no_of_comments = self.get_value_from_element(no_of_comments_element, "textContent")
                if no_of_comments is not None:
                    self.logger.info(f"Found no of comments {no_of_comments}")
                    return no_of_comments
                else:
                    return 0
  

    def filter_textcontent(self,comment):
        """Filetring the scrapped text content """
        filters = list(':/.%#@&*()!-_=+ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890? ')
        comment = comment.split(" ")
        comment = " ".join(comment)
        comment = comment.replace("\n", " ")
        for i in range(0, len(comment)):
            if comment[i] not in filters:
                comment = comment.replace(comment[i], " ")
        return comment

    def get_loaded_comments(self):
        """
        :return: str
        """
        self.logger.info("Scrolling to load comments")
        #time.sleep(1)
        self.driver.execute_script("window.scrollTo(0,500);")
        self.logger.info("Fetching no of comments")
        no_of_comments = self.find_no_of_comments()
        no_of_comments = int(no_of_comments.replace(" ","").replace(",","").strip())
        if no_of_comments > 100:
            self.logger.info(f"No of comments are: {no_of_comments} higher than 200, Selecting first 100 only.")
            no_of_comments = 100
        i = 0
        while i < no_of_comments/2:
            length = self.driver.execute_script("return window.scrollY")
            self.driver.execute_script("window.scrollTo(arguments[0],arguments[0]+300);", length)
            #time.sleep(1)
            i += 1
        #time.sleep(1)
        # #new code
        # scroll_length = no_of_comments * 50
        # length = self.driver.execute_script("return window.scrollY")
        # self.driver.execute_script("window.scrollTo(arguments[0],arguments[0]+arguments[1]);", length,scroll_length)
        # time.sleep(1)
        # #---------------
        self.logger.info("Scroll completed")
        return no_of_comments


    def get_comment_data(self):
        """
        :return: list(Dict)
        """
        commenters_names = None
        comments = None
        commenters_elements = self.get_many_website_elements(By.CSS_SELECTOR,
                                                             self.selector_store.get_video_commenters_name_css())
        if commenters_elements is not None:
            commenters_names = [self.get_value_from_element(element, "textContent")
                                for element in commenters_elements]
        comments_elements = self.get_many_website_elements(By.CSS_SELECTOR,
                                                           self.selector_store.get_video_comments_css())
        if comments_elements is not None:
            comments = [self.get_value_from_element(element, "textContent") for element in comments_elements]
        comment_data = []
        if commenters_names is not None and comments is not None:
            for name, comment in zip(commenters_names, comments):
                if name is not None and comment is not None:
                    name = name.replace(".", " ")  #mongo db does not allow . in key
                    name = name.replace("@", "")
                    comment_data.append({name.strip(): comment})
            self.logger.info(f"Comment scrapped : {comment_data}")
        print(len(comment_data))
        return comment_data


    def scrap_video_details(self,link):
        """
        :param link:link of video
        :param video_obj: object of video class
        :param document_obj: objject of mongodocument class
        :return:None
        """
        self.open_video_link(link)
        time.sleep(2)
        youtuber_name = self.find_youtuber_name()
        print("Youtuber name:",youtuber_name)

        video_title = self.get_title_of_video()
        print("Video title:",video_title)

        self.logger.info("Scrolling to load comments")
        no_of_comments = self.get_loaded_comments()
        print("No.of Comments:",no_of_comments)
        data = self.get_comment_data()
        comment_data = {video_title:data}
        #print("All comments:",comment_data)

        obj = MongoOperations(mongo_uri=MONGO_URI)
        obj.insert_document_into_collection(comment_data)

        return (link,youtuber_name,video_title,no_of_comments,data)

    def process_request(self):
        """
        :return: tuple of result of scrapping: (link,youtuber_name,video_title,no_of_comments,comment_data:dict)
        """
        result = self.scrap_video_details(self.youtube_video_link)
        self.driver.close()
        return result

if __name__ == "__main__":
    obj = Scrapper("https://www.youtube.com/watch?v=vIIOsQyjdaU")
    obj.process_request()












