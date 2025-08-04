document.querySelectorAll('form').forEach(form => {
  form.querySelectorAll('button[name="action"]').forEach(button => {
    button.addEventListener('click', function (e) {
      // Remove "clicked" from others
      form.querySelectorAll('button[name="action"]').forEach(btn => btn.removeAttribute('clicked'));
      this.setAttribute('clicked', true);

      if (this.value === 'delete') {
        // Remove required from all except faculty_id before form validation
        form.querySelectorAll('input, select').forEach(input => {
          if (input.name !== 'faculty_id') {
            input.removeAttribute('required');
          }
        });
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('select').forEach(select => {
    select.addEventListener('focus', () => {
      select.style.borderColor = '#2980b9';
    });
    select.addEventListener('blur', () => {
      select.style.borderColor = '#ccc';
    });
  });
});

// Clone and add new time slot
  function addTimeSlot() {
    const container = document.getElementById('time-slots-container');
    const firstSlot = container.querySelector('.time-slot');
    const newSlot = firstSlot.cloneNode(true);

    // Reset all selects to default
    newSlot.querySelectorAll('select').forEach(select => select.selectedIndex = 0);

    // Add event listener to new remove button
    newSlot.querySelector('.remove-btn').addEventListener('click', function () {
      removeSlot(this);
    });

    container.appendChild(newSlot);
  }

  // Remove a time slot
  function removeSlot(button) {
    const container = document.getElementById('time-slots-container');
    if (container.querySelectorAll('.time-slot').length > 1) {
      button.closest('.time-slot').remove();
    }
  }

  // Ensure existing Remove buttons work on page load
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.remove-btn').forEach(btn => {
      btn.addEventListener('click', () => removeSlot(btn));
    });
  });


let totalClassrooms = 0;
let currentIndex = 0;
let classroomData = [];

function prepareSingleClassroomEntry() {
  totalClassrooms = parseInt(document.getElementById("num_classrooms").value);
  classroomData = Array.from({ length: totalClassrooms }, (_, i) => ({
    name: `Classroom ${i + 1}`,
    seating: [80, 85, 90][i % 3],
    ownership: "Owned",
    students: "",
    day: "",
    start_time: "",
    end_time: ""
  }));

  let rentedIndexes = [];
  while (rentedIndexes.length < Math.min(5, totalClassrooms)) {
    let idx = Math.floor(Math.random() * totalClassrooms);
    if (!rentedIndexes.includes(idx)) rentedIndexes.push(idx);
  }
  for (let idx of rentedIndexes) {
    classroomData[idx].ownership = "Rented";
  }

  currentIndex = 0;
  renderClassroomInput();
}

function renderClassroomInput() {
  const c = classroomData[currentIndex];

  document.getElementById("single-classroom-entry").innerHTML = `
    <h3>${c.name}</h3>
    <p><strong>Seating Capacity:</strong> ${c.seating}</p>
    <p><strong>Ownership:</strong> ${c.ownership}</p>

    <label><strong>Allotted Students:</strong></label>
    <input type="number" name="students[]" min="0" value="${c.students}" required>

    <label><strong>Select Day:</strong></label>
    <select name="classroom_days[]" required>
      <option value="" disabled selected>Select Day</option>
      ${dayList.map(day => `<option value="${day}" ${c.day === day ? 'selected' : ''}>${day}</option>`).join('')}
    </select>

    <label><strong>Start Time:</strong></label>
    <select name="start_times[]" required>
      <option value="" disabled selected>Select Time</option>
      ${timeList.map(time => `<option value="${time}" ${c.start_time === time ? 'selected' : ''}>${time}</option>`).join('')}
    </select>

    <label><strong>End Time:</strong></label>
    <select name="end_times[]" required>
      <option value="" disabled selected>Select Time</option>
      ${timeList.map(time => `<option value="${time}" ${c.end_time === time ? 'selected' : ''}>${time}</option>`).join('')}
    </select>

    <input type="hidden" name="classroom_names[]" value="${c.name}">
    <input type="hidden" name="seating_capacities[]" value="${c.seating}">
    <input type="hidden" name="ownerships[]" value="${c.ownership}">
    <p><em>Classroom ${currentIndex + 1} of ${totalClassrooms}</em></p>
  `;
}

function nextClassroom() {
  saveCurrentClassroomData();
  if (currentIndex < totalClassrooms - 1) {
    currentIndex++;
    renderClassroomInput();
  }
}

function prevClassroom() {
  saveCurrentClassroomData();
  if (currentIndex > 0) {
    currentIndex--;
    renderClassroomInput();
  }
}

function saveCurrentClassroomData() {
  const students = document.querySelector('input[name="students[]"]').value;
  const day = document.querySelector('select[name="classroom_days[]"]').value;
  const startTime = document.querySelector('select[name="start_times[]"]').value;
  const endTime = document.querySelector('select[name="end_times[]"]').value;

  classroomData[currentIndex].students = students;
  classroomData[currentIndex].day = day;
  classroomData[currentIndex].start_time = startTime;
  classroomData[currentIndex].end_time = endTime;
}

function addCourseSlot() {
  const container = document.getElementById("course-block-container");
  const firstBlock = container.querySelector(".course-block");
  const newBlock = firstBlock.cloneNode(true);

  // Clear all selects and inputs except hidden faculty index
  newBlock.querySelectorAll("select").forEach(sel => {
    sel.selectedIndex = 0;
  });

  newBlock.querySelectorAll("input").forEach(inp => {
    if (inp.type !== "hidden") inp.value = "";
  });

  // Reset time slots to just one
  const containerSlot = newBlock.querySelector(".time-slots-container");
  const allSlots = containerSlot.querySelectorAll(".time-slot");
  allSlots.forEach((slot, i) => {
    if (i === 0) {
      slot.querySelectorAll("select").forEach(sel => sel.selectedIndex = 0);
    } else {
      slot.remove();
    }
  });

  // Remove existing Select2 instance before appending
  const facultySelect = newBlock.querySelector('.faculty-select');
  if (facultySelect && $(facultySelect).hasClass("select2-hidden-accessible")) {
    $(facultySelect).select2('destroy');
  }

  container.appendChild(newBlock);      // ✅ Add the new block
  updateFacultyFieldNames();           // ✅ Re-index faculty[] names
  initializeSelect2();                 // ✅ Apply Select2 to new dropdown
}

function removeCourseSlot(button) {
  const container = document.getElementById("course-block-container");
  if (container.children.length > 1) {
    button.closest(".course-block").remove();
    updateFacultyFieldNames();  // ✅ fix indexes after removal
  }
}

function addTimeSlot(addBtn) {
  const courseBlock = addBtn.closest(".course-block");
  const container = courseBlock.querySelector(".time-slots-container");
  const firstSlot = container.querySelector(".time-slot");
  const newSlot = firstSlot.cloneNode(true);

  newSlot.querySelectorAll("select").forEach(sel => sel.selectedIndex = 0);
  container.appendChild(newSlot);
}

function removeSlot(button) {
  const container = button.closest(".time-slots-container");
  if (container.children.length > 1) {
    button.closest(".time-slot").remove();
  }
}

function injectAllClassroomInputs() {
  // Save the currently displayed classroom's inputs
  saveCurrentClassroomData();

  // Clear previously injected inputs
  document.querySelectorAll('.injected-input').forEach(e => e.remove());

  const form = document.getElementById("capacity-form");

  classroomData.forEach((c, index) => {
    // ✅ Skip incomplete rows
    if (!c.day || !c.start_time || !c.end_time || !c.students) {
      return;  // Don't inject if any field is empty
    }

    const fields = {
      "classroom_names[]": c.name,
      "seating_capacities[]": c.seating,
      "ownerships[]": c.ownership,
      "students[]": c.students,
      "classroom_days[]": c.day,
      "start_times[]": c.start_time,
      "end_times[]": c.end_time
    };

    for (let name in fields) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = name;
      input.value = fields[name];
      input.classList.add("injected-input");
      form.appendChild(input);
    }
  });

  return true;
}



document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("capacity-form");

  if (form) {
    form.addEventListener("submit", function (e) {
      injectAllClassroomInputs(); // ← Inject all classroom entries
    });
  }
});

function updateFacultyFieldNames() {
  document.querySelectorAll('.course-block').forEach((block, index) => {
    const facultySelect = block.querySelector('.faculties-dropdown');
    if (facultySelect) {
      facultySelect.setAttribute('name', `faculties[${index}][]`);
    }

    const indexField = block.querySelector('input[name="faculty_indexes[]"]');
    if (indexField) {
      indexField.value = index;
    }
  });
}

function initializeSelect2() {
  $('.faculty-select').select2({
    placeholder: "Select Faculties",
    allowClear: true,
    width: '100%'
  });
}

document.addEventListener("DOMContentLoaded", function () {
  updateFacultyFieldNames();  // ✅ assign names on initial load
  initializeSelect2();        // ✅ init select2 on page load
});




  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("capacity-form");
    const deleteButton = form.querySelector('button[name="action"][value="delete"]');

    deleteButton.addEventListener("click", () => {
      const visibleClassroom = document.querySelector('input[name="students[]"]');
      const classroomName = document.querySelector('input[name="classroom_names[]"]').value;
      const day = document.querySelector('select[name="classroom_days[]"]').value;
      const start = document.querySelector('select[name="start_times[]"]').value;
      const end = document.querySelector('select[name="end_times[]"]').value;

      document.getElementById("delete_classroom_name").value = classroomName;
      document.getElementById("delete_classroom_day").value = day;
      document.getElementById("delete_start_time").value = start;
      document.getElementById("delete_end_time").value = end;
    });
  });


    // facultyData will be injected from Jinja template
let facultyData = {};
