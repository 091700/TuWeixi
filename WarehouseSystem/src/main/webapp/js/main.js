function showDialog(actionType, goodsId = 0) {
    const dialog = document.getElementById('goodsDialog');
    const form = dialog.querySelector('form');
    
    if (actionType === 'add') {
        form.reset();
        form.elements['action'].value = 'add';
        form.elements['id'].value = '0';
        dialog.querySelector('#dialogTitle').textContent = '新增商品';
    } else {
        fetch(`/goods?action=get&id=${goodsId}`)
            .then(response => response.json())
            .then(data => {
                form.elements['name'].value = data.name;
                form.elements['specification'].value = data.specification;
                form.elements['quantity'].value = data.quantity;
                form.elements['price'].value = data.price;
                form.elements['action'].value = 'update';
                form.elements['id'].value = data.id;
                dialog.querySelector('#dialogTitle').textContent = '编辑商品';
            });
    }
    dialog.style.display = 'block';
}

function closeDialog() {
    document.getElementById('goodsDialog').style.display = 'none';
}

function confirmDelete(goodsId) {
    if (confirm('确定要删除这个商品吗？')) {
        const form = document.createElement('form');
        form.method = 'post';
        form.action = '/goods';
        
        const actionInput = document.createElement('input');
        actionInput.type = 'hidden';
        actionInput.name = 'action';
        actionInput.value = 'delete';
        
        const idInput = document.createElement('input');
        idInput.type = 'hidden';
        idInput.name = 'id';
        idInput.value = goodsId;
        
        form.appendChild(actionInput);
        form.appendChild(idInput);
        document.body.appendChild(form);
        form.submit();
    }
}

window.onclick = function(event) {
    const dialog = document.getElementById('goodsDialog');
    if (event.target === dialog) {
        dialog.style.display = 'none';
    }
}