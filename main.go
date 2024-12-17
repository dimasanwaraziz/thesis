package main

import (
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
)

// Fungsi untuk menyembunyikan pesan dalam gambar
func embedMessageInImage(img image.Image, message string) (image.Image, error) {
	width := img.Bounds().Dx()
	height := img.Bounds().Dy()
	encodedImg := image.NewRGBA(img.Bounds())

	messageBytes := []byte(message)
	messageIndex := 0
	bitIndex := 0

	// Iterasi untuk setiap pixel dan sembunyikan pesan
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			originalColor := img.At(x, y)
			r, g, b, a := originalColor.RGBA()

			// Menyembunyikan satu bit pesan dalam bit terkecil dari warna RGB
			if messageIndex < len(messageBytes) {
				// Ambil bit pesan berikutnya
				messageBit := (messageBytes[messageIndex] >> (7 - bitIndex)) & 1

				// Modifikasi nilai warna berdasarkan bit pesan
				r = (r & 0xFFFE) | uint32(messageBit) // Ubah bit terkecil R
				b = (b & 0xFFFE) | uint32(messageBit) // Ubah bit terkecil B
				g = (g & 0xFFFE) | uint32(messageBit) // Ubah bit terkecil G

				bitIndex++
				if bitIndex > 7 {
					bitIndex = 0
					messageIndex++
				}
			}

			encodedImg.Set(x, y, color.RGBA{
				R: uint8(r),
				G: uint8(g),
				B: uint8(b),
				A: uint8(a),
			})
		}
	}

	return encodedImg, nil
}

// Fungsi untuk menyimpan gambar PNG
func saveImage(img image.Image, filename string) error {
	outFile, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer outFile.Close()
	return png.Encode(outFile, img)
}

// Fungsi untuk membaca gambar PNG
func loadImage(filename string) (image.Image, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	return png.Decode(file)
}

// Fungsi enkripsi Polar Code sederhana (contoh sangat dasar)
func encryptWithPolarCode(message string) string {
	// Untuk kesederhanaan, kita hanya melakukan XOR dengan kunci tetap (sebagai substitusi dari algoritma polar code yang sebenarnya)
	key := []byte("polarcodekey")
	encryptedMessage := make([]byte, len(message))

	for i := 0; i < len(message); i++ {
		encryptedMessage[i] = message[i] ^ key[i%len(key)]
	}

	return string(encryptedMessage)
}

// Fungsi untuk mendekripsi pesan
func decryptWithPolarCode(encryptedMessage string) string {
	// Melakukan XOR dengan kunci yang sama untuk dekripsi
	key := []byte("polarcodekey")
	decryptedMessage := make([]byte, len(encryptedMessage))

	for i := 0; i < len(encryptedMessage); i++ {
		decryptedMessage[i] = encryptedMessage[i] ^ key[i%len(key)]
	}

	return string(decryptedMessage)
}

func main() {
	// Pesan yang akan disembunyikan
	message := "This is a secret message"
	encryptedMessage := encryptWithPolarCode(message)

	// Membaca gambar yang ingin digunakan untuk steganografi
	img, err := loadImage("input.png")
	if err != nil {
		fmt.Println("Error loading image:", err)
		return
	}

	// Menyembunyikan pesan yang telah dienkripsi dalam gambar
	encodedImg, err := embedMessageInImage(img, encryptedMessage)
	if err != nil {
		fmt.Println("Error embedding message:", err)
		return
	}

	// Menyimpan gambar yang telah dienkripsi
	err = saveImage(encodedImg, "encoded_image.png")
	if err != nil {
		fmt.Println("Error saving image:", err)
		return
	}

	// Menampilkan pesan asli dan pesan yang terdekripsi
	fmt.Println("Original Message:", message)
	fmt.Println("Encrypted Message:", encryptedMessage)

	// Ekstrak dan dekode pesan dari gambar
	// (Fungsi untuk ekstraksi pesan tidak termasuk dalam contoh ini, tapi bisa diterapkan mirip dengan proses encoding)
	decryptedMessage := decryptWithPolarCode(encryptedMessage)
	fmt.Println("Decrypted Message:", decryptedMessage)
}
