import requests
from datetime import datetime, timedelta
import asyncio
from db_api import Database


class Canvas():
    current_term = "Fall 2023"
    baseURL = "https://canvas.instructure.com/api/v1/"

    def __init__(self, userid, token, canvasid):
        self.userid = userid
        self.token = token
        self.canvasid = canvasid
        self.header = {'Authorization': 'Bearer ' + self.token}

    @classmethod
    async def create(cls, userid):
        userInfo = await Database().getUserInfo(userid)
        token = userInfo[0]
        canvasid = userInfo[1]
        return cls(userid, token, canvasid)

    async def getUserID(self):
        r = requests.get(f"{self.baseURL}/users/self", headers=self.header)
        r = r.json()
        return r['id']

    async def verifyToken(self):
        r = requests.get(
            f"{self.baseURL}/users/self", headers=self.header)

        return (not r.status_code == 401, r.json()['short_name'])

    def convertTime(time):
        newtime = time.replace("T", " ")
        newtime = newtime.replace("Z", "")  # ? remove excess letters

        time_object = datetime.strptime(newtime, '%Y-%m-%d %H:%M:%S')
        time_object -= timedelta(hours=5)  # ? adjust for time difference (EST)

        return time_object.timestamp()

    async def getCourses(self):

        data = {
            "enrollment_type": "student",
            "enrollment_state": "active",
            "per_page": 30,
            "include[]": "term"
        }
        r = requests.get(
            f"{self.baseURL}users/{self.canvasid}/courses", headers=self.header, data=data).json()

        courses = []

        for i in range(len(r)-1):
            if r[i]["term"]["name"] == self.current_term:
                courses.append(r[i])

        return courses

    async def getAssignments(self):
        url = "https://canvas.instructure.com/api//v1/users/{}/courses/{}/assignments"
        params = {
            "per_page": 30,
        }

        response = requests.get(
            f"{self.baseURL}/users/{self.userid}/todo", headers=self.header, params=params)

        if response.status_code == 200:
            to_do_list = response.json()

            # Display the fetched to-do items
            for idx, item in enumerate(to_do_list, start=1):
                assignment = item.get("assignment")
                if assignment:
                    assignment_name = assignment.get("name")
                    due_date = assignment.get("due_at")
                    course_id = assignment.get("course_id")
                    print(
                        f"{idx}. Assignment: {assignment_name}, Due Date: {due_date}, Course ID: {course_id}")
        else:
            print(f"Error: {response.status_code}")

    # get current grades of student
    async def getGrades(self, courses):
        data = {
            "per_page": 15,
            "state[]": "active"
        }
        grades = []
        r = requests.get(
            f"{self.baseURL}/users/{self.userid}/enrollments", headers=self.header, data=data)
        r = r.json()

        for course in courses.items():
            for enrollment in r:
                if enrollment['course_id'] == course[1]['id']:
                    grades.append({
                        "course": course[0],
                        "grade": enrollment["grades"]['current_score']
                    })
        return grades

    async def submitAssignment(self, courseID, assignmentID, fileURL):
        header = {'Authorization': 'Bearer ' + self.token(self.userid)}

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
    async def aggregateOne(self, courses):
        # get all courses associated with token
        userCourses = exit

        # compare with the courses already present. courses is list of IDs

        # return courses that are not present (name and ID)

        pass


async def main():
    canvas = await Canvas.create(492179045379866634)

    test = await canvas.getCourses()
    print("Courses:\n")
    print(test)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())