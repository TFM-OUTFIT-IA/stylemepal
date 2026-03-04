import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpEventType } from '@angular/common/http';
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


  showBatchModal = false;
  batchFiles: File[] = [];
  batchProgress = 0;          
  batchStatus: 'idle' | 'uploading' | 'processing' | 'done' | 'error' = 'idle';
  batchMessage = '';
  batchAccepted = 0;
  batchRejected = 0;

  constructor(private itemService: ItemService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.cargarItems();
  }

  cargarItems() {
    this.itemService.getItems().subscribe((data) => {
      this.items = data;
      this.cdr.detectChanges();
    });
  }

  getImageUrl(imagePath: string): string {
    const cleanPath = imagePath.split('?')[0];
    return `${cleanPath}?t=${new Date().getTime()}`;
  }

  onAddClick() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.onchange = (event: any) => {
      const file = event.target.files[0];
      if (file) {
        const nombre = prompt("Nombre para esta prenda:", file.name.replace(/\.[^.]+$/, '')) || file.name;
        this.itemService.createItem(file, nombre).subscribe(() => {
          this.cargarItems();
        });
      }
    };
    fileInput.click();
  }

  onFolderClick() {
    const folderInput = document.createElement('input');
    folderInput.type = 'file';
    folderInput.accept = 'image/*';
    folderInput.multiple = true;
    (folderInput as any).webkitdirectory = true;
    (folderInput as any).directory = true;

    folderInput.onchange = (event: any) => {
      const files: File[] = Array.from(event.target.files).filter((f: any) =>
        f.type.startsWith('image/')
      ) as File[];

      if (files.length === 0) {
        alert('No se encontraron imágenes en la carpeta seleccionada.');
        return;
      }

      this.batchFiles = files;
      this.batchProgress = 0;
      this.batchStatus = 'idle';
      this.batchMessage = '';
      this.batchAccepted = 0;
      this.batchRejected = 0;
      this.showBatchModal = true;
      this.cdr.detectChanges();
    };
    folderInput.click();
  }

  startBatchUpload() {
    if (this.batchFiles.length === 0) return;

    this.batchStatus = 'uploading';
    this.batchProgress = 0;
    this.cdr.detectChanges();

    this.itemService.uploadBatch(this.batchFiles).subscribe({
      next: (event: any) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.batchProgress = Math.round(100 * event.loaded / event.total);
          this.cdr.detectChanges();
        } else if (event.type === HttpEventType.Response) {
          const body = event.body;
          this.batchStatus = 'processing';
          this.batchMessage = body.message;
          this.batchAccepted = body.item_ids?.length ?? 0;
          const rejMatch = body.message.match(/Rejected (\d+)/);
          this.batchRejected = rejMatch ? parseInt(rejMatch[1]) : 0;
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        this.batchStatus = 'error';
        this.batchMessage = err.error?.detail ?? 'Error al subir las imágenes.';
        this.cdr.detectChanges();
      }
    });
  }

  closeBatchModal() {
    this.showBatchModal = false;
    if (this.batchStatus === 'processing' || this.batchStatus === 'done') {
      this.cargarItems();
    }
    this.batchFiles = [];
    this.batchStatus = 'idle';
  }
  
  onViewClick(item: any) {
    alert(`Nombre: ${item.name}\nCategoría: ${item.category}\nEstilo: ${item.style}\nTiempo: ${item.weather}\nGénero: ${item.gender}`);
  }

  onEditClick(item: any) {
    const nuevoNombre = prompt("Editar nombre:", item.name);
    if (nuevoNombre && nuevoNombre !== item.name) {
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
    const nuevoEstado = !item.clean;
    this.itemService.updateItem(item.id, { limpio: nuevoEstado }).subscribe(() => {
      item.clean = nuevoEstado;
      this.cdr.detectChanges();
    });
  }

  onCleanAllClick() {
    if (confirm("¿Marcar TODAS las prendas como limpias?")) {
      this.itemService.cleanAllItems().subscribe(() => {
        this.cargarItems();
      });
    }
  }
}