import csv
from time import sleep
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class XPATH:
    search_field_xpath = '/html/body/div/div[1]/div[1]/div[3]/div/div[1]/div/label/div/div[2]'
    chat_field_xpath = '/html/body/div/div[1]/div[1]/div[4]/div[1]/footer/div[1]/div[2]/div/div[2]'

class Recipient:
    def __init__(self, first_name: str, last_name: str, full_name: str, contact_no: str) -> None:
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.full_name: str = full_name
        self.contact_no: str = contact_no

class WhatsApp:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome('./src/driver/chromedriver')
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.maximize_window()
        self.driver.get('https://web.whatsapp.com/')
        with open('./src/message.txt', 'r') as msg_file:
            self.message = msg_file.read()

    def parse_contact_no(contact_no: str) -> str:
        pass

    @staticmethod
    def recipient_data(filename: str) -> List[Recipient]:
        '''
        Returns a list of information about the recipient(s).
        '''
        data = []
        with open(filename, 'r') as recipient_data_file:
            recipient_csv = csv.DictReader(recipient_data_file)
            for recipient in recipient_csv:
                recipient = Recipient(
                    first_name=recipient['First Name'].strip(),
                    last_name=recipient['Last Name'].strip(),
                    full_name=' '.join([recipient['First Name'], recipient['Last Name']]).replace(' ', ''),
                    contact_no=recipient['Mobile']
                )
                data.append(recipient)
        return data

    def search_person(self, contact_no: str) -> None:
        self.wait.until(presence_of_all_elements_located((By.XPATH, XPATH.search_field_xpath)))
        search_field = self.driver.find_element_by_xpath(XPATH.search_field_xpath)
        search_field.clear()
        search_field.send_keys(contact_no)
        # Adding some sleep time because the chat takes some time to appear and also it adds some human feel to it.
        sleep(3)
    
    def select_person(self, full_name: str) -> None:
        person_chat_xpath = '//span[@title=' + '"' + full_name + '"' + ']'
        print(person_chat_xpath)
        self.wait.until(presence_of_all_elements_located((By.XPATH, person_chat_xpath)))
        person_chat = self.driver.find_element_by_xpath(person_chat_xpath)
        person_chat.click()
    
    def send_message(self, first_name: str, sender_name: str) -> None:
        self.wait.until(presence_of_all_elements_located((By.XPATH, XPATH.chat_field_xpath)))
        chat_field = self.driver.find_element_by_xpath(XPATH.chat_field_xpath)
        chat_field.clear()
        self.message = f'Hi {first_name},\n{self.message},\nThanks, {sender_name}'
        message_array: List[str] = self.message.split('\n')
        for msg in message_array:
            chat_field.send_keys(msg)
            chat_field.send_keys(Keys.SHIFT + Keys.ENTER)
        chat_field.send_keys(Keys.ENTER)
        sleep(0.5)
    
    def run(self, filename: str, sender_name: str) -> None:
        recipients: List[Recipient] = self.recipient_data(filename=filename)
        print(recipients)
        failures_file = open('./src/failures.csv', 'a')
        failures_csv = csv.writer(failures_file)
        for recipient in recipients:
            self.search_person(contact_no=recipient.contact_no)
            try:
                self.select_person(full_name=recipient.full_name)
            except Exception as e:
                failures_csv.writerow([recipient.full_name, recipient.contact_no])
                print(f'Failed for {recipient.full_name}')
                print(str(e))
                continue
            self.send_message(first_name=recipient.first_name, sender_name=sender_name)
        failures_file.close()


if __name__ == '__main__':
    sender_name: str = input('Enter the name of the sender')
    WhatsApp().run(filename='./src/recipients.csv', sender_name=sender_name)