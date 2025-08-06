// ------------------------------
// Handle form button actions (like delete)
// ------------------------------
document.querySelectorAll('form').forEach(form => {
  form.querySelectorAll('button[name="action"]').forEach(button => {
    button.addEventListener('click', function () {
      form.querySelectorAll('button[name="action"]').forEach(btn => btn.removeAttribute('clicked'));
      this.setAttribute('clicked', true);

      if (this.value === 'delete') {
        form.querySelectorAll('input, select').forEach(input => {
          if (input.name !== 'faculty_id') {
            input.removeAttribute('required');
          }
        });
      }
    });
  });
});

// ------------------------------
// Add focus styles for selects
// ------------------------------
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('select').forEach(select => {
    select.addEventListener('focus', () => select.classList.add('select-focused'));
    select.addEventListener('blur', () => select.classList.remove('select-focused'));
  });
});

// ------------------------------
// Add/Remove Time Slots with animation
// ------------------------------
function addTimeSlot(addBtn = null) {
  const container = addBtn
    ? addBtn.closest(".course-block").querySelector(".time-slots-container")
    : document.getElementById('time-slots-container');

  const firstSlot = container.querySelector('.time-slot');
  const newSlot = firstSlot.cloneNode(true);

  newSlot.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
  newSlot.classList.add('fade-in');

  const removeBtn = newSlot.querySelector('.remove-btn');
  removeBtn.addEventListener('click', () => removeSlot(removeBtn));

  container.appendChild(newSlot);
}

function removeSlot(button) {
  const container = button.closest(".time-slots-container");
  if (container.querySelectorAll(".time-slot").length > 1) {
    button.closest(".time-slot").classList.add('fade-out');
    setTimeout(() => {
      button.closest(".time-slot").remove();
    }, 300);
  }
}

// ------------------------------
// Handle course block duplication
// ------------------------------
function addCourseSlot() {
  const container = document.getElementById("course-block-container");
  const firstBlock = container.querySelector(".course-block");
  const newBlock = firstBlock.cloneNode(true);

  newBlock.querySelectorAll("select").forEach(sel => sel.selectedIndex = 0);
  newBlock.querySelectorAll("input").forEach(inp => {
    if (inp.type !== "hidden") inp.value = "";
  });

  // Reset time slots to one
  const slotContainer = newBlock.querySelector(".time-slots-container");
  slotContainer.querySelectorAll(".time-slot").forEach((slot, i) => {
    if (i === 0) {
      slot.querySelectorAll("select").forEach(sel => sel.selectedIndex = 0);
    } else {
      slot.remove();
    }
  });

  // Fix Select2
  const facultySelect = newBlock.querySelector('.faculty-select');
  if (facultySelect && $(facultySelect).hasClass("select2-hidden-accessible")) {
    $(facultySelect).select2('destroy');
  }

  container.appendChild(newBlock);
  updateFacultyFieldNames();
  initializeSelect2();
}

function removeCourseSlot(button) {
  const container = document.getElementById("course-block-container");
  if (container.children.length > 1) {
    button.closest(".course-block").remove();
    updateFacultyFieldNames();
  }
}

// ------------------------------
// Dynamic Classroom Input Logic
// ------------------------------
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
  rentedIndexes.forEach(idx => classroomData[idx].ownership = "Rented");

  currentIndex = 0;
  renderClassroomInput();
}

function renderClassroomInput() {
  const c = classroomData[currentIndex];

  document.getElementById("single-classroom-entry").innerHTML = `
    <div class="classroom-card fade-in">
      <h3>${c.name}</h3>
      <p><strong>Seating:</strong> ${c.seating}</p>
      <p><strong>Ownership:</strong> ${c.ownership}</p>

      <label>Students</label>
      <input type="number" name="students[]" value="${c.students}" required>

      <label>Day</label>
      <select name="classroom_days[]" required>
        <option disabled selected>Select</option>
        ${dayList.map(day => `<option value="${day}" ${c.day === day ? 'selected' : ''}>${day}</option>`).join('')}
      </select>

      <label>Start Time</label>
      <select name="start_times[]" required>
        <option disabled selected>Select</option>
        ${timeList.map(time => `<option value="${time}" ${c.start_time === time ? 'selected' : ''}>${time}</option>`).join('')}
      </select>

      <label>End Time</label>
      <select name="end_times[]" required>
        <option disabled selected>Select</option>
        ${timeList.map(time => `<option value="${time}" ${c.end_time === time ? 'selected' : ''}>${time}</option>`).join('')}
      </select>

      <input type="hidden" name="classroom_names[]" value="${c.name}">
      <input type="hidden" name="seating_capacities[]" value="${c.seating}">
      <input type="hidden" name="ownerships[]" value="${c.ownership}">
      <p><em>Classroom ${currentIndex + 1} of ${totalClassrooms}</em></p>
    </div>
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
  const start = document.querySelector('select[name="start_times[]"]').value;
  const end = document.querySelector('select[name="end_times[]"]').value;

  Object.assign(classroomData[currentIndex], { students, day, start_time: start, end_time: end });
}

// ------------------------------
// Inject all classroom inputs before form submission
// ------------------------------

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

// ------------------------------
// Submit Hook
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("capacity-form");
  if (form) {
    form.addEventListener("submit", injectAllClassroomInputs);
  }
});

// ------------------------------
// Update dynamic faculty[] naming
// ------------------------------
function updateFacultyFieldNames() {
  document.querySelectorAll('.course-block').forEach((block, index) => {
    const select = block.querySelector('.faculties-dropdown');
    if (select) select.setAttribute('name', `faculties[${index}][]`);

    const indexField = block.querySelector('input[name="faculty_indexes[]"]');
    if (indexField) indexField.value = index;
  });
}

// ------------------------------
// Initialize Select2 dropdowns
// ------------------------------
function initializeSelect2() {
  $('.faculty-select').select2({
    placeholder: "Select Faculties",
    allowClear: true,
    width: 'resolve'  
    
  });
}
// ------------------------------
// Dashboard Navigation Tabs (Updated)
// ------------------------------

document.addEventListener("DOMContentLoaded", () => {
  const deleteBtn = document.querySelector('#capacity-form button[name="action"][value="delete"]');
  const form = document.getElementById("capacity-form");

  if (deleteBtn && form) {
    deleteBtn.addEventListener('click', (event) => {
      event.preventDefault();  // ⛔️ Prevent auto-submit

      saveCurrentClassroomData();  // Save current UI state

      const card = document.querySelector('.classroom-card');
      const day = card?.querySelector('select[name="classroom_days[]"]')?.value;
      const start = card?.querySelector('select[name="start_times[]"]')?.value;
      const end = card?.querySelector('select[name="end_times[]"]')?.value;
      const location = document.querySelector('#location')?.value;
      const classroomName = `Classroom ${currentIndex + 1}`;  // Adjust to match actual sheet values
      console.log("✅ Deleting classroom:", classroomName, "at", location, "on", day, start, end);


      

      // Fill hidden fields
      document.getElementById('delete_classroom_name').value = classroomName || '';
      document.getElementById('delete_classroom_day').value = day || '';
      document.getElementById('delete_start_time').value = start || '';
      document.getElementById('delete_end_time').value = end || '';

      // ✅ Show in console for debug
      console.log("🧪 Delete values:", { location, classroomName, day, start, end });

      if (!location || !classroomName || !day || !start || !end) {
        alert("❌ Please ensure all fields are selected before deleting.");
        return;
      }

      // ✅ Now submit the form
      form.submit();
    });
  }
});

// Fix button click tracking
document.querySelectorAll('#capacity-form button[value]').forEach(button => {
  button.addEventListener('click', function () {
    const actionInput = document.getElementById('form-action') || document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.id = 'form-action';
    actionInput.value = this.value;
    document.getElementById('capacity-form').appendChild(actionInput);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => initializeSelect2(), 10); // ⏳ Let layout settle
});
