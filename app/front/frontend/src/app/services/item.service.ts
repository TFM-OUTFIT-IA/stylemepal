import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ItemService {
  private apiUrl = '/api/v1/items';

  constructor(private http: HttpClient) {}

  getItems(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  createItem(image: File, nombre: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', image);
    formData.append('nombre', nombre);
    return this.http.post<any>(this.apiUrl, formData);
  }

  updateItem(id: string, data: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, data);
  }

  deleteItem(id: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`);
  }

  cleanAllItems(): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/bulk/clean-all`, {});
  }

  confirmOutfit(ids: string[]): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/bulk/dirty`, { ids });
  }

  getRecommendation(style: string, weather: string, gender: string, anchorId?: string, excludeIds?: string[]): Observable<any> {
    let params: any = { style, weather, gender };
    if (anchorId) params.anchor_id = anchorId;
    if (excludeIds && excludeIds.length > 0) params.exclude_ids = excludeIds; 
    
    return this.http.get<any>(`${this.apiUrl}/recommend`, { params });
  }

  uploadBatch(files: File[]): Observable<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file, file.name));
    return this.http.post<any>(`${this.apiUrl}/batch`, formData, {
      reportProgress: true,
      observe: 'events',
    });
  }

  askAgent(prompt: string): Observable<any> {
    return this.http.post<any>('/api/v1/agent/generate', { prompt });
  }
}