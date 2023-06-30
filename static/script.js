
window.addEventListener("load", function() {
   const attributesElem = document.getElementById('attributes')
   const listsElem = document.getElementById('lists')
   const dictionariesElem = document.getElementById('dictionaries')
   
   function getValue(id) {
      returnValue = ''
      try {
	 returnValue = JSON.parse(document.getElementById(id).textContent);
      } catch (error) {}

      return returnValue
   }

   const effects = {}
   let attributes = getValue('item.attributes');
   let lists = getValue('item.lists');
   let dictionaries = getValue('item.dictionaries');
   const data_types = getValue('data_types');

   attributesElem.innerHTML = ''
   listsElem.innerHTML = ''
   dictionariesElem.innerHTML = ''

   console.log(attributes)
   console.log(lists)
   console.log(dictionaries)
   console.log(data_types)

   function addElementRemover(button, element) {
      button.addEventListener("click", function() {
         let context = element.id.split('.')
	  console.log(context)

         if (context.length === 2) {
            if(context[0] === 'attribute') {
	       delete attributes[context[1]]
            } else if (context[0] === 'list') {
	       delete lists[context[1]]
	    } else if (context[0] === 'dictionary') {
	       delete dictionaries[context[1]]
	    }
         }

	 else if (context.length === 3) {
             if (context[0] === 'dictionary') {
	        delete dictionaries[context[1]][context[2]]
	     }
         }

	 element.remove();
      });
   }

   function addAttributes() {
      attributesElem.innerHTML += `<span>`

      let addHTML = ''

      for (let key in attributes) {
	 if (key === 'name') {
            addHTML += `
	       <li>
		 Name: <input type="text" name="name" value="${attributes[key]}"></input>
	       </li>`
	    console.log(attributesElem)
         } else if (key === 'data_type') {
	   optionsHTML = `<option value="${attributes[key]}"> ${attributes[key]} </option>`
	   for (let data_type of data_types) {
	      if (data_type !== attributes[key]) {
	         optionsHTML += `<option value="${data_type}"> ${data_type} </option>`
	      }
	   }

	   addHTML += `
	      <li>
	        Data_type: <select name="data_type">
		   ${optionsHTML}
		</select>
	      </li>`
        } else {
	   addHTML += `
	      <li id="attribute.${key}">
	        <button class="removeElement" type="button" value="attribute.${key}">X</button>
	        ${key}: <input type="text" name="attribute.${key}" value="${attributes[key]}"></input>
	      </li>`
        }

      } 

      attributesElem.innerHTML += `
        <span>
	   ${addHTML}
	</span>

        <li>
	  <button type="button" id="addAttribute">Add</button>
	</li>`
   }

   function addAttribute() {
      let key = window.prompt('Attribute: ');

      if (!(key in attributes)) {
	attributes[key] = 'added'

        let li = document.createElement('li')
        let button = document.createElement('button')
	let input = document.createElement('input')

	li.id=`attribute.${key}`

	button.type='button'
	button.id = `attribute.${key}.remove`
	button.textContent = 'X'

	input.type = 'text'
	input.name = `attribute.${key}`
        
        let items = attributesElem.childNodes
	let lastAttribute = items[items.length - 3];
        
	lastAttribute.appendChild(li)
        li.appendChild(button)
	li.append(`${key}: `)
	li.appendChild(input)

      	addElementRemover(button, li);
      }
   }

   function addLists() {
      for (let key in lists) {
	 itemsHTML = ''
	 list = lists[key]

	 for (let index in list) {
	    id = `list.${key}.${index}`
	    itemsHTML += `
	       <td id="${id}">
	         <button class="removeElement" type="button" value="${id}">X</button>
	         <input type="text" name="${id}" value="${list[index]}"></input>
	       </td>`
	 }

         listsElem.innerHTML += `
	    <span id="list.${key}">
	    <h2>
	      <button class="removeElement" type="button" value="list.${key}">X</button>
	      ${key}
	    </h2>

	    <table>
	       <tr>
	         ${itemsHTML}
	       </tr>
	    </table>

	    <button type="button" class="addListItem" value="list.${key}">Add</button>
	    </span>`
      }
   }

   function addListItem(listElem) {
      let title = listElem.id.split('.')[1]
      let list = lists[title]
      let index = list.length

      let id = `list.${title}.${index}`

      list[index] = 'added'

      let items = listElem.childNodes
      let table = items[items.length-4].children[0].children[0] 
	   
      let td = document.createElement('td')
      let button = document.createElement('button')
      let input = document.createElement('input')

      td.id = `${id}`

      button.type='button'
      button.id=`${id}.remove`
      button.textContent = 'X'

      input.type='text'
      input.name=`${id}`

      td.appendChild(button)
      td.appendChild(input)

      table.appendChild(td)

      let tableItem = document.getElementById(`${id}`)
      let removeButton = document.getElementById(`${id}.remove`)

      addElementRemover(button, td)
   }

   function addList() {
      let title = window.prompt('List: ').trim();
      
      if (lists === '') { lists = [] } 

      if (title !== '' && !(title in lists)) {
	 console.log(title)
         lists[title] = ['added']

	 listsElem.innerHTML += `
	    <span id="list.${title}">
	    <h2>
	       <button type="button" id="list.${title}.remove">X</button>
	       ${title}
	    </h2>

            <table>
	       <tr>
	       </tr>
	    </table>

	    <button type="button" id="list.${title}.add">Add</button>
	    </span>`

	 let button = document.getElementById(`list.${title}.remove`);
	 let element = document.getElementById(`list.${title}`);
	
	 addElementRemover(button, element);

	 let addButton = document.getElementById(`list.${title}.add`);
	 addButton.addEventListener('click', function(){
	    addListItem(element)
	 });
      }
   }

   function addDictionaryItem(dictionaryElem) {
       let key = window.prompt('Item: ').trim()
       let title = dictionaryElem.id.split('.')[1]
       let dictionary = dictionaries[title]

       if (!(key in dictionary) && key !== '') {
          dictionary[key] = 'added'
          
	  let li = document.createElement('li')
	  let button = document.createElement('button')
	  let input = document.createElement('input')

	  li.id=`dictionary.${title}.${key}`

	  button.type='button'
	  button.id=`dictionary.${title}.${key}.remove`
	  button.textContent = 'X'

	  input.type='text'
	  input.name=`dictionary.${title}.${key}`

	  li.appendChild(button)
	  li.append(`${key}: `)
	  li.appendChild(input)

	  dictionaryElem.appendChild(li)

	  addElementRemover(button, li)
       }
   }

   function addEffect() {
      title = ''
      
      for (let i = 1; i <= 50; i++) {
         if (!(`effect${String(i)}` in effects)){
	    title = `effect${String(i)}`
            effects[title] = 'added'
            i = 100
         }
      }

      dictionariesElem.innerHTML += `
         <span id="dictionary.${title}">
	 <h2>
	    <button type="button" id="dictionary.${title}.remove">X</button>
	    ${title}
	 </h2>

	 <ul style="list-style-type: none;">
	   <li>
	      target:
	      <input type="text" name="dictionary.${title}.target"></input>
	   </li>

		 <li>
		 e_type:
		 <select name="dictionary.${title}.e_type">
		    <option value="add" selected>Add</option>
              <option value="sub">Subtract</option>
              <option value="set">Set</option>
		 </select>
		 </li>

           <li>
	      resource:
	      <input type="text" name="dictionary.${title}.resource"></input>
           </li>

           <li>
	      amount:
	      <input type="text" name="dictionary.${title}.amount"></input>
	    </li>
	 </ul>
         </span>`

      removeButton = document.getElementById(`dictionary.${title}.remove`)
      effectElem = document.getElementById(`dictionary.${title}`);

      addElementRemover(removeButton, effectElem)
   }

   function addDictionary() {
      let title = window.prompt('Dictionary: ').trim()

      if (dictionaries === '') { dictionaries = {} }

      if (title !== '' && !(title in dictionaries) && !(title.toLowerCase().includes('effect'))
         && !(title.toLowerCase().includes('outcomes'))) {
	 console.log('test')
         dictionaries[title] = {'default': 'added'}

	 dictionariesElem.innerHTML += `
	    <span id="dictionary.${title}">
            <h2>
	      <button type="button" id="dictionary.${title}.remove">X</button>
	      ${title}
	    </h2>
	      <ul style="list-style-type: none;" id="dictionary.${title}.list">
	      </ul>

              <button type="button" id="dictionary.${title}.add">Add</button>
	    </span>`

         let removeButton = document.getElementById(`dictionary.${title}.remove`);
	 let element = document.getElementById(`dictionary.${title}`);

	 addElementRemover(removeButton, element);

	 let listElem = document.getElementById(`dictionary.${title}.list`);
	 let addButton = document.getElementById(`dictionary.${title}.add`);
	 addButton.addEventListener('click', function() {
             addDictionaryItem(listElem);
         });
      }
   }

   function addDictionaries() {
      if (attributes.data_type === 'encounter') {
         for (let title in dictionaries) {
	    if (title.includes('effect')) {
	       effects[title] = 'added';
               
	       dictionaryHTML = ''
	       for (let key in dictionaries[title]){
		  value = dictionaries[title][key]

			if (key === 'e_type') {
				dictionaryHTML += `
				<li>
		 		e_type:
		 		<select name="dictionary.${title}.e_type">
		    			<option value="add" selected>Add</option>
              			<option value="sub">Subtract</option>
              			<option value="set">Set</option>
		 		</select>
		 		</li>
				`
			}

			else {
	          	dictionaryHTML += `
		     	<li>
		        	${key}: 
				<input type="text" name="dictionary.${title}.${key}" value=${value}></input>
		     	</li>`
			}
	       }

	       dictionariesElem.innerHTML += `
	          <span id="dictionary.${title}">
	          <h2>
		     <button class="removeElement" type="button" value="dictionary.${title}">X</button>
		     ${title}
		  </h2>
		    <ul style="list-style-type: none;">
		      ${dictionaryHTML}
		    </ul>
		  </span>`
	    }
	 }
      }

      for (let title in dictionaries) {
	    if (!title.includes('effect')) {
               dictionaryHTML = ''
	       for (let key in dictionaries[title]){
		  value = dictionaries[title][key]
	          dictionaryHTML += `
		     <li id="dictionary.${title}.${key}">
		        <button class="removeElement" type="button" value="dictionary.${title}.${key}">X</button>
		        ${key}: 
			<input type="text" name="dictionary.${title}.${key}" value="${value}"></input>
		     </li>`
	       }

	       dictionariesElem.innerHTML += `
	          <span id="dictionary.${title}">
	          <h2>
		     <button class="removeElement" type="button" value="dictionary.${title}">X</button>
		     ${title}
		  </h2>

		    <ul style="list-style-type: none;" id="dictionary.${title}.list">
		      ${dictionaryHTML}
		    </ul>

		    <button type="button" class="addDictionaryItem" value="dictionary.${title}">Add</button>
		  </span>`
	    }
	 }
   }

   function addButtons() {
      const buttons = document.getElementsByClassName('removeElement');
      
      for (let button of buttons) {
	 console.log(button.value)
         let element = document.getElementById(button.value);
	 console.log(element)
         addElementRemover(button, element)
      }

     const listAddButtons = document.getElementsByClassName('addListItem');

     for (let button of listAddButtons) {
	 let element = document.getElementById(button.value);
	 button.addEventListener('click', function() {
            addListItem(element)
         });
     }

     const dictionaryAddButtons = document.getElementsByClassName('addDictionaryItem');

     for (let button of dictionaryAddButtons) {
        let element = document.getElementById(`${button.value}.list`);
	button.addEventListener('click', function() {
           addDictionaryItem(element)
        });
     }
   }

   function addDefaultForms() {
     addAttributes()

     if (lists) {
        addLists()
     } if (dictionaries) {
        addDictionaries()
     }

     addButtons()
   }

   addDefaultForms()

   const addAttributeButton = document.getElementById('addAttribute');
   addAttributeButton.addEventListener('click', addAttribute)

   const addListButton = document.getElementById('addList');
   addListButton.addEventListener('click', addList);

   const addDictionaryButton = document.getElementById('addDictionary');
   addDictionaryButton.addEventListener('click', addDictionary);

   const addEffectButton = document.getElementById('addEffect')
   if (addEffectButton) {
      addEffectButton.addEventListener('click', addEffect);
   }
});
