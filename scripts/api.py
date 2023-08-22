import requests
from datetime import datetime, timedelta
import aiohttp
import asyncio
import time
import scripts.db_api as db_api 

class Canvas():
    current_term = "Fall 2023"
    baseURL = "https://canvas.instructure.com/api/v1"


    token = lambda userID: db_api.getToken(userID)

    async def getUserID(self, token):
        header = {'Authorization': 'Bearer ' + token}
        r = requests.get(
            f"{self.baseURL}/users/self", headers=header)
        r = r.json()
        return r['id']

    async def verifyToken(self, token):
        header = {'Authorization': 'Bearer ' + token}
        r = requests.get(
            f"{self.baseURL}/users/self", headers=header)

        return (not r.status_code == 401, r.json()['short_name'])

    def convertTime(time):
        newtime = time.replace("T", " ")
        newtime = newtime.replace("Z", "")  # ? remove excess letters

        time_object = datetime.strptime(newtime, '%Y-%m-%d %H:%M:%S')
        time_object -= timedelta(hours=5)  # ? adjust for time difference (EST)

        return time_object.timestamp()

    async def getCourses(self, userID: None, auth_token: None):
        if not userID and not auth_token: return

        if userID:
            header = {'Authorization': 'Bearer ' + self.token(userID)}
        else:
            header = {'Authorization': 'Bearer ' + auth_token}
        data = {
            "enrollment_type": "student",
            "enrollment_state": "active",
            "per_page": 30,
            "include[]": "term"
        }
        r = requests.get(
            f"{self.baseURL}users/{userID}/courses", headers=header, data=data).json()

        courses = []

        for i in range(len(r)-1):
            if r[i]["term"]["name"] == self.current_term:
                courses.append(r[i])

        

        return courses

    async def getAssignments(self, userID):
        header = {'Authorization': 'Bearer ' + self.token(userID)}
        url = "https://canvas.instructure.com/api//v1/users/{}/courses/{}/assignments"
        params = {
            "per_page": 30,
        }

        response = requests.get(f"{self.baseURL}/users/{userID}/todo",headers=header,params=params)

        if response.status_code == 200:
            to_do_list = response.json()

            # Display the fetched to-do items
            for idx, item in enumerate(to_do_list, start=1):
                assignment = item.get("assignment")
                if assignment:
                    assignment_name = assignment.get("name")
                    due_date = assignment.get("due_at")
                    course_id = assignment.get("course_id")
                    print(f"{idx}. Assignment: {assignment_name}, Due Date: {due_date}, Course ID: {course_id}")
        else:
            print(f"Error: {response.status_code}")

    # get current grades of student
    async def getGrades(self, courses, userID):
        header = {'Authorization': 'Bearer ' + self.token(userID)}
        data = {
            "per_page": 15,
            "state[]": "active"
        }
        grades = []
        r = requests.get(
            f"{self.baseURL}/users/{userID}/enrollments", headers=header, data=data)
        r = r.json()

        for course in courses.items():
            for enrollment in r:
                if enrollment['course_id'] == course[1]['id']:
                    grades.append({
                        "course": course[0],
                        "grade": enrollment["grades"]['current_score']
                    })
        return grades

    async def submitAssignment(self, userID, courseID, assignmentID, fileURL):
        header = {'Authorization': 'Bearer ' + self.token(userID)}
        
        response = requests.get(fileURL)

        if response.status_code == 200:
            fileContent = response.content

            files = {
                "submission[file]": ("filename.txt", fileContent),
            }

            response = requests.post(
                f"{self.baseURL}/courses/{courseID}/assignments/{assignmentID}/submissions",
                headers=header,
                files=files
            )

            if response.status_code == 200:
                submissionInfo = response.json()
                return True
            else:
                return False

    #  if token does not have overlapping courses  
    async def aggregateOne(self, token, courses):
        # get all courses associated with token
        userCourses = exit

        # compare with the courses already present. courses is list of IDs
        
        # return courses that are not present (name and ID) 

        pass



def main():
    canvas = Canvas()

    test = Canvas()
