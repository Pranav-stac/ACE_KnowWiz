from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests
import os
import base64
from datetime import datetime
import time

class ChromaImageScraper:
    def __init__(self):
        # Setup Chrome options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(options=self.options)
        
        # Create downloads directory if it doesn't exist
        self.download_dir = 'downloaded_images'
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def get_generated_image(self, prompt):
        try:
            print("Navigating to website...")
            self.driver.get('https://chroma-neon.vercel.app/')
            
            print("Entering prompt...")
            prompt_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea.flex'))
            )
            prompt_input.clear()
            prompt_input.send_keys(prompt)
            time.sleep(1)
            
            print("Pressing Enter to generate image...")
            prompt_input.send_keys(Keys.RETURN)
            
            print("Waiting for image generation (this may take up to 30 seconds)...")
            time.sleep(5)
            
            try:
                image_element = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'img'))
                )
                
                # Wait a bit to ensure image is fully loaded
                time.sleep(2)
                
                # Get the image source
                image_src = image_element.get_attribute('src')
                print("Found image data")
                
                if image_src:
                    # Handle base64 image
                    if image_src.startswith('data:image'):
                        # Extract the base64 data
                        import base64
                        # Remove the data URL prefix (e.g., 'data:image/png;base64,')
                        base64_data = image_src.split(',')[1]
                        
                        # Decode base64 to binary
                        image_data = base64.b64decode(base64_data)
                        
                        # Save the image
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{self.download_dir}/chroma_{timestamp}.png"
                        
                        with open(filename, 'wb') as f:
                            f.write(image_data)
                        print(f"Image successfully saved: {filename}")
                        return filename
                        
                    # Handle regular URL
                    elif image_src.startswith('http'):
                        response = requests.get(image_src)
                        if response.status_code == 200:
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"{self.download_dir}/chroma_{timestamp}.png"
                            with open(filename, 'wb') as f:
                                f.write(response.content)
                            print(f"Image successfully downloaded: {filename}")
                            return filename
                    
                    print("Invalid image source format")
                    return None
                
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return None
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            try:
                self.driver.save_screenshot(f"{self.download_dir}/error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                print("Error screenshot saved")
            except:
                print("Could not save error screenshot")
            return None
        
    def close(self):
        self.driver.quit()

    def show_image(self, image_path):
        try:
            from PIL import Image
            image = Image.open(image_path)
            image.show()
        except ImportError:
            print("PIL (Pillow) library not installed. Cannot display image.")
        except Exception as e:
            print(f"Could not display image: {str(e)}")

def main():
    scraper = ChromaImageScraper()
    try:
        prompt = "Person at a hackathon"
        downloaded_image = scraper.get_generated_image(prompt)
        if downloaded_image:
            print(f"Image saved to: {downloaded_image}")
            scraper.show_image(downloaded_image)  # Display the image
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 