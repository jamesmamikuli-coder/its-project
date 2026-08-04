import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

function StudentManagementPage() {
  const changeRole = async (id, currentRole) => {

  try {

    const newRole =
      currentRole === "admin"
      ? "student"
      : "admin";

    await axios.put(
      `http://127.0.0.1:5000/api/update-role/${id}`,
      {
        role: newRole
      }
    );

    setStudents(

      students.map((student) =>

        student.id === id
          ? {
              ...student,
              role: newRole
            }
          : student

      )

    );

    alert(
      "Role updated successfully ✅"
    );

  } catch (error) {

    console.log(error);

    alert(
      "Role update failed ❌"
    );

  }

};
const deleteStudent = async (id) => {

  try {

    await axios.delete(
      `http://127.0.0.1:5000/api/delete-student/${id}`
    );

    setStudents(
      students.filter(
        (student) => student.id !== id
      )
    );

    alert("Student deleted successfully ✅");

  } catch (error) {

    console.log(error);

    alert("Failed to delete student ❌");

  }

};
  const role = localStorage.getItem("role");

  if (role !== "admin") {

    return (
      <h1>
        Access Denied ❌
      </h1>
    );
  }

  const [students, setStudents] = useState([]);

  useEffect(() => {

    axios
      .get("http://127.0.0.1:5000/api/students")

      .then((res) => {

        setStudents(res.data.students);

      })

      .catch((err) => {

        console.log(err);

      });

  }, []);

  return (

    <div style={{ padding: "20px" }}>

      <h1>
        👥 Student Management
      </h1>

      <table
        border="1"
        cellPadding="10"
        style={{
          borderCollapse: "collapse",
          width: "100%"
        }}
      >

        <thead>

          <tr>

            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Created</th>
            <th>View</th>
            <th>Delete</th>
            <th>Role Action</th>

          </tr>

        </thead>

        <tbody>

          {
            students.map((student) => (

              <tr key={student.id}>

                <td>{student.id}</td>

                <td>{student.username}</td>

                <td>{student.email}</td>

                <td>{student.role}</td>

                <td>{student.created_at}</td>

                <td>

                  <Link
                    to={`/student-performance/${student.username}`}
                  >
                    View
                  </Link>
                  <td>

  <button
    onClick={() =>
      changeRole(
        student.id,
        student.role
      )
    }
  >

    {
      student.role === "admin"
        ? "Make Student"
        : "Make Admin"
    }

  </button>

</td>
                  <td>

  <button
    onClick={() =>
      deleteStudent(student.id)
    }
  >
    Delete
  </button>

</td>

                </td>

              </tr>

            ))
          }

        </tbody>

      </table>

    </div>

  );
}

export default StudentManagementPage;