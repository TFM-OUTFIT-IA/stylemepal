import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ItemService } from '../../services/item.service';

@Component({
  selector: 'app-coleccion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './colection.component.html',
  styleUrls: ['./colection.component.css']
})
export class ColectionComponent implements OnInit {
  items: any[] = [];

  constructor(private itemService: ItemService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.cargarItems();
  }

  cargarItems() {
    this.itemService.getItems().subscribe((data) => {
      const timestamp = new Date().getTime();
      
      this.items = data.map(item => ({
        ...item,
        image_path: `${item.image_path}?t=${timestamp}`
      }));

      // Forzar dectección de cambios por espera a la api
      this.cdr.detectChanges(); 
    });
  }


  onAddClick() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.onchange = (event: any) => {
      const file = event.target.files[0];
      if (file) {
        const nombreSimulado = prompt("Introduce un nombre de prueba para este modelo:", "Modelo IA 1") || "Modelo IA 1";
        this.itemService.createItem(file, nombreSimulado).subscribe(() => {
          this.cargarItems(); 
        });
      }
    };
    fileInput.click();
  }

  onViewClick(item: any) {
    alert(`Datos del modelo:\nNombre: ${item.nombre}`);
  }

  onEditClick(item: any) {
    const nuevoNombre = prompt("Editar nombre:", item.nombre);
    if (nuevoNombre && nuevoNombre !== item.nombre) {
      this.itemService.updateItem(item.id, { nombre: nuevoNombre }).subscribe(() => {
        this.cargarItems();
      });
    }
  }

  onDeleteClick(item: any) {
    if (confirm("¿Estás seguro de que deseas eliminar este elemento?")) {
      this.itemService.deleteItem(item.id).subscribe(() => {
        this.cargarItems();
      });
    }
  }

  toggleEstadoLimpio(item: any) {
    const nuevoEstado = !item.limpio;
    
    this.itemService.updateItem(item.id, { limpio: nuevoEstado }).subscribe(() => {
      item.limpio = nuevoEstado;
      this.cdr.detectChanges(); 
    });
  }


  onCleanAllClick() {
    if (confirm("¿Estás seguro de que quieres marcar TODAS las prendas como limpias?")) {
      this.itemService.cleanAllItems().subscribe(() => {
        this.cargarItems();
      });
    }
  }
}