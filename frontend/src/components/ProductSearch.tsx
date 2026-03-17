'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Image from 'next/image';

interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  price: number;
  image_url: string;
  description: string;
}

interface SearchResult {
  product: Product;
  similarity_score: number;
  explanation: string;
  match_details: any;
}

interface SearchResponse {
  results: SearchResult[];
  total_found: number;
  processing_time: number;
  api_cost_estimate: number;
}

export default function ProductSearch() {
  const [image, setImage] = useState<File | null>(null);
  const [textQuery, setTextQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7);
  const [brandFilter, setBrandFilter] = useState('');
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [processingTime, setProcessingTime] = useState(0);
  const [apiCost, setApiCost] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setImage(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const handleSearch = async () => {
    if (!image && !textQuery.trim()) {
      alert('Please provide an image or text query');
      return;
    }

    setLoading(true);
    setResults([]);

    try {
      const formData = new FormData();
      if (image) {
        formData.append('image', image);
      }
      if (textQuery.trim()) {
        formData.append('text_query', textQuery);
      }
      formData.append('confidence_threshold', confidenceThreshold.toString());
      if (brandFilter) {
        formData.append('brand_filter', brandFilter);
      }
      if (priceMin) {
        formData.append('price_min', priceMin);
      }
      if (priceMax) {
        formData.append('price_max', priceMax);
      }

      const response = await fetch('http://localhost:8001/search', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data: SearchResponse = await response.json();
      setResults(data.results);
      setProcessingTime(data.processing_time);
      setApiCost(data.api_cost_estimate);
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => {
    setImage(null);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">
          Multi-Cloud Multimodal Product Search
        </h1>
        <p className="text-gray-600 text-center">
          Upload an image or describe what you're looking for
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">Product Image</label>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              {image ? (
                <div className="relative">
                  <Image
                    src={URL.createObjectURL(image)}
                    alt="Uploaded product"
                    width={200}
                    height={200}
                    className="mx-auto rounded-lg object-cover"
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      clearImage();
                    }}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div>
                  <div className="text-4xl mb-2">📷</div>
                  <p className="text-gray-600">
                    {isDragActive ? 'Drop the image here' : 'Drag & drop an image, or click to select'}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">PNG, JPG, WebP up to 10MB</p>
                </div>
              )}
            </div>
          </div>

          {/* Text Query and Filters */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Text Description</label>
              <textarea
                value={textQuery}
                onChange={(e) => setTextQuery(e.target.value)}
                placeholder="Describe the product you're looking for..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Brand Filter</label>
                <input
                  type="text"
                  value={brandFilter}
                  onChange={(e) => setBrandFilter(e.target.value)}
                  placeholder="e.g., Nike, Adidas"
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Confidence Threshold</label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={confidenceThreshold}
                  onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="text-xs text-gray-500 text-center mt-1">
                  {confidenceThreshold}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Min Price</label>
                <input
                  type="number"
                  value={priceMin}
                  onChange={(e) => setPriceMin(e.target.value)}
                  placeholder="0"
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Max Price</label>
                <input
                  type="number"
                  value={priceMax}
                  onChange={(e) => setPriceMax(e.target.value)}
                  placeholder="1000"
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-8 py-3 rounded-lg font-medium transition-colors"
          >
            {loading ? 'Searching...' : 'Search Products'}
          </button>
        </div>
      </div>

      {/* Results */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Analyzing your search...</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="mb-4 text-center text-sm text-gray-600">
          Found {results.length} results in {processingTime.toFixed(2)}s
          (Est. cost: ${apiCost.toFixed(4)})
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {results.map((result) => (
          <div key={result.product.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="relative h-48">
              <Image
                src={result.product.image_url}
                alt={result.product.name}
                fill
                className="object-cover"
              />
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-1">{result.product.name}</h3>
              <p className="text-gray-600 mb-2">{result.product.brand}</p>
              <p className="text-green-600 font-bold mb-2">${result.product.price}</p>
              <div className="text-sm text-gray-500 mb-2">
                Similarity: {(result.similarity_score * 100).toFixed(1)}%
              </div>
              <details className="text-sm">
                <summary className="cursor-pointer font-medium text-blue-600 hover:text-blue-800">
                  Why this match?
                </summary>
                <p className="mt-2 text-gray-700">{result.explanation}</p>
              </details>
            </div>
          </div>
        ))}
      </div>

      {results.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          No results found. Try adjusting your search criteria.
        </div>
      )}
    </div>
  );
}